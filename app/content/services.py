import os, json, subprocess, shlex
from django.conf import settings
from django.apps import apps

def _run(cmd, log_path=None):
    if log_path:
        with open(log_path, 'w', encoding='utf-8', errors='ignore') as f:
            p = subprocess.Popen(shlex.split(cmd), stdout=f, stderr=subprocess.STDOUT)
            p.wait()
            return p.returncode
    p = subprocess.run(shlex.split(cmd), capture_output=True)
    return p.returncode

def _probe(path):
    out = subprocess.check_output(shlex.split(
        f'ffprobe -v error -print_format json -show_streams -show_format "{path}"'
    ))
    j = json.loads(out.decode('utf-8', 'ignore'))
    v = next((s for s in j.get('streams', []) if s.get('codec_type') == 'video'), None)
    fps = 25.0
    if v and v.get('avg_frame_rate') and v['avg_frame_rate'] != '0/0':
        num, den = v['avg_frame_rate'].split('/')
        fps = float(num) / float(den)
    return {
        'width': int(v.get('width') or 0) if v else 0,
        'height': int(v.get('height') or 0) if v else 0,
        'fps': fps,
        'duration': float(j.get('format', {}).get('duration') or 0.0),
    }

def process_video(pk: str):
    Video = apps.get_model('content', 'Video')
    v = Video.objects.get(pk=pk)

    # сразу ставим processing
    Video.objects.filter(pk=pk).update(status='processing', error='')

    src_abs = os.path.join(settings.MEDIA_ROOT, v.source.name)
    if not os.path.exists(src_abs):
        Video.objects.filter(pk=pk).update(status='failed', error=f'source not found: {src_abs}')
        return

    try:
        meta = _probe(src_abs)
    except Exception as e:
        Video.objects.filter(pk=pk).update(status='failed', error=str(e))
        return

    out_rel = v.out_dir or f'video/{v.pk}/'
    out_abs = os.path.join(settings.MEDIA_ROOT, out_rel)
    os.makedirs(out_abs, exist_ok=True)

    # постер делаем «best effort»
    poster_rel = f'video/posters/{v.pk}.jpg'
    poster_abs = os.path.join(settings.MEDIA_ROOT, poster_rel)
    os.makedirs(os.path.dirname(poster_abs), exist_ok=True)
    subprocess.call(shlex.split(f'ffmpeg -y -i "{src_abs}" -frames:v 1 -q:v 3 "{poster_abs}"'))

    # HLS
    fps = max(1.0, float(meta.get('fps') or 25.0))
    gop = int(round(fps * 2))
    seg = 4
    segpat = os.path.join(out_abs, 'chunk_%05d.m4s')
    m3u8   = os.path.join(out_abs, 'master.m3u8')
    log    = os.path.join(out_abs, 'ffmpeg.log')

    cmd = (
      f'ffmpeg -y -i "{src_abs}" '
      f'-c:v libx264 -preset veryfast -profile:v high -level 4.1 -pix_fmt yuv420p '
      f'-g {gop} -keyint_min {gop} -sc_threshold 0 '
      f'-c:a aac -b:a 160k -ar 48000 -ac 2 -movflags +faststart '
      f'-hls_time {seg} -hls_segment_type fmp4 '
      f'-hls_fmp4_init_filename init.mp4 '
      f'-hls_segment_filename "{segpat}" '
      f'-hls_flags independent_segments '
      f'-hls_playlist_type vod "{m3u8}"'
    )
    code = _run(cmd, log_path=log)

    # финализация: если артефакты есть — ставим ready, иначе failed
    has_m3u8 = os.path.exists(m3u8)
    seg_count = len([f for f in os.listdir(out_abs) if f.endswith('.m4s')])
    poster_exists = os.path.exists(poster_abs)

    if has_m3u8 and seg_count > 0 and code == 0:
        # одно атомарное обновление — исключаем гонки и «устаревший» инстанс
        Video.objects.filter(pk=pk).update(
            meta=meta,
            poster=(poster_rel if poster_exists else ''),
            m3u8_url=f"{settings.MEDIA_URL}{out_rel}master.m3u8",
            out_dir=out_rel,
            status='ready',
            error=''
        )
    else:
        err = 'no playlist/segments created' if not has_m3u8 or seg_count == 0 else 'ffmpeg exited non-zero'
        Video.objects.filter(pk=pk).update(status='failed', error=err)

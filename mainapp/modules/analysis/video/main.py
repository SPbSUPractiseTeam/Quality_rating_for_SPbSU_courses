from .content.video import Video
from .content.video_review import set_video_length, get_videos_pages, set_video_review
from .content.video_watched_percent import set_watched_percent

from .output import output as out


def execute(cursor, _course_name, _path):
    # Initialize videos
    pages = get_videos_pages(cursor)
    videos = []
    for page in pages:
        video = Video(page)
        videos.append(video)
    set_video_length(cursor, videos)
    set_video_review(cursor, videos)
    set_watched_percent(cursor, videos)

    # Output
    return out.output(videos, _course_name, _path)

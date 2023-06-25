from create_idea import create_idea, normalize_idea, manipulate_idea
from create_caption import create_caption 
from upload_instagram import upload_instagram
from create_image import create_image
from create_video import create_video

decision_tree = {
    "create idea": (create_idea, ["target_segment", "program_description"]),
    "normalize idea": (normalize_idea, ["user_idea", "target_segment", "program_description"]),
    "manipulate idea": (manipulate_idea, ["idea"]),
    "create image": (create_image, ["idea", "styles"]),
    "create caption": (create_caption, ["idea"]),
    "upload instagram": (upload_instagram, ["image_url", "caption"]),
    "create video": (create_video, ["idea", "tone"])
}
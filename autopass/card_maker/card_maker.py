__all__ = ()

import os

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

font = PIL.ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), "Wadik.otf"),
    90,
)


class ImageEditor:
    def __init__(
        self,
        template_path: str,
        output_path: str,
        circle_size: tuple[int, int] = (300, 300),
        photo_position: tuple[int, int] = (100, 200),
        text_position: tuple[int, int] = (300, 300),
    ):
        self.template_path = template_path
        self.output_path = output_path
        self.circle_size = circle_size
        self.photo_position = photo_position
        self.text_position = text_position

    def create_rounded_image(self, photo_path: str):
        def prepare_mask(antialias=2):
            mask = PIL.Image.new(
                "L",
                (self.circle_size[0] * antialias, self.circle_size[1] * antialias),
                0,
            )
            PIL.ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
            return mask.resize(self.circle_size, PIL.Image.LANCZOS)

        def crop(im, s):
            w, h = im.size
            k = w / s[0] - h / s[1]
            offset = h * 0.5
            if k > 0:
                im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
            elif k < 0:
                top = max(0, (h - w) / 2 - offset)
                bottom = top + w
                im = im.crop((0, top, w, bottom))

            return im.resize(s, PIL.Image.LANCZOS)

        im = PIL.Image.open(photo_path)
        im = crop(im, self.circle_size)
        im.putalpha(prepare_mask())
        return im

    def put_photo_in_template(self, image: PIL.Image.Image):
        im = PIL.Image.open(self.template_path)
        im.paste(
            image,
            self.photo_position,
            mask=image,
        )
        return im

    def draw_text_on_image(
        self,
        image: PIL.Image.Image,
        text: str,
        final_name: str,
    ):
        draw = PIL.ImageDraw.Draw(image)
        draw.text(self.text_position, text, (8, 37, 103), font, angle=90)
        os.makedirs(self.output_path, exist_ok=True)
        image.save(f"{self.output_path}/{final_name}")
        return image

    def create_final_image(
        self,
        image_path: str,
        text: str,
        final_name: str,
    ):

        rounded_image = self.create_rounded_image(image_path)

        template_with_photo = self.put_photo_in_template(rounded_image)

        return self.draw_text_on_image(
            template_with_photo,
            text,
            final_name,
        )

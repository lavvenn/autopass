__all__ = ()

from PIL import Image

from card_maker import ImageEditor


# Создаем тестовые файлы
def create_test_files():
    test_photo = Image.new("RGB", (400, 600), color=(100, 150, 200))
    test_photo.save("test_photo.jpg")

    template = Image.new("RGB", (800, 600), color=(255, 255, 200))
    template.save("template.png")


def test_image_editor():
    create_test_files()

    editor = ImageEditor(
        template_path="template.png",
        output_path="output",
        circle_size=(250, 250),
        photo_position=(50, 100),
        text_position=(350, 400),
    )

    editor.create_final_image(
        image_path="test_photo.jpg",
        text="IVANOV I.I.",
        final_name="result.png",
    )


if __name__ == "__main__":
    test_image_editor()

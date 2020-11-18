import os, json

from PIL import Image

class SpriteGenerator:

    def generate(path):
        images = []
        widthTotal = 0
        maxHeight = 0
        sprites = {}

        # Load all icon image
        for root, dirs, files in os.walk(path, topdown=False):
            for file in files:
                image = Image.open(root+'/'+file)
                images.append(image)
                widthTotal += image.size[0]
                if maxHeight < image.size[1]:
                    maxHeight = image.size[1]

        # Generate big image
        bigImage = Image.new('RGBA', (widthTotal, maxHeight), (255,0,0,0))
        pointer = 0
        # Paste icon to big image
        for image in images:
            sprite = {
                'width': image.size[0],
                'height': image.size[1],
                'x': pointer,
                'y': 0,
                'pixelRatio': 1,
                'visible': True
            }
            bigImage.paste(image, (pointer, 0))
            pointer += image.size[0]
            imageName = image.filename.split('.')[0].split('/')[-1]
            sprites[imageName] = sprite

        # Save
        f = open(path + '/sprite.json','w')
        f.write(json.dumps(sprites))
        f.close()
        bigImage.save(path + '/sprite.png','PNG')
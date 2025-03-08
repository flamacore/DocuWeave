from PIL import Image, ImageDraw

def create_branch_closed():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw white arrow pointing right
    draw.line([(6, 4), (10, 8), (6, 12)], fill=(255, 255, 255), width=2)
    img.save('resources/branch-closed.png')

def create_branch_open():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw white arrow pointing down
    draw.line([(4, 6), (8, 10), (12, 6)], fill=(255, 255, 255), width=2)
    img.save('resources/branch-open.png')

def create_branch_line():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw white vertical line
    draw.line([(8, 0), (8, 16)], fill=(255, 255, 255), width=1)
    img.save('resources/vline.png')
    img.save('resources/branch-more.png')  # Used for middle items
    img.save('resources/branch-end.png')   # Used for last items

if __name__ == '__main__':
    create_branch_closed()
    create_branch_open()
    create_branch_line()
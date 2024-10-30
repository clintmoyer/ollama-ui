import cairo
import math

# Set up the SVG surface and context
width, height = 100, 100  # Size of the icon
surface = cairo.SVGSurface("convo.svg", width, height)
context = cairo.Context(surface)

# Move the origin to the center and rotate by 45 degrees clockwise
context.translate(width / 2, height / 2)
context.rotate(math.radians(45))
context.translate(-width / 2, -height / 2)

# Set the color and line width for the outline
context.set_source_rgb(0, 0, 0)  # Black outline color
context.set_line_width(3)

# Draw the pencil shaft as a vertical rectangle outline
shaft_x, shaft_y = width * 0.4, height * 0.2
shaft_width, shaft_height = width * 0.1, height * 0.5
context.rectangle(shaft_x, shaft_y, shaft_width, shaft_height)
context.stroke()

# Draw the pencil tip as an outlined triangle at the bottom
context.move_to(shaft_x, shaft_y + shaft_height)  # Bottom left of the shaft
context.line_to(shaft_x + shaft_width, shaft_y + shaft_height)  # Bottom right of the shaft
context.line_to(shaft_x + shaft_width / 2, shaft_y + shaft_height + 15)  # Point of the tip
context.close_path()
context.stroke()

# Draw the eraser as a small rectangle outline at the top of the shaft
eraser_x, eraser_y = shaft_x, shaft_y - 10
eraser_width, eraser_height = shaft_width, 10
context.rectangle(eraser_x, eraser_y, eraser_width, eraser_height)
context.stroke()

# Finish and save the SVG file
surface.finish()
print("SVG icon created as 'convo.svg'")

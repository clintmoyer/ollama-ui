import cairo

# Set up the SVG surface and context
width, height = 100, 100  # Size of the icon
surface = cairo.SVGSurface("collapse.svg", width, height)
context = cairo.Context(surface)

# Draw rounded rectangle for the background
corner_radius = 15
context.set_line_width(3)
context.set_source_rgba(0, 0, 0, 0)  # Fully transparent background
context.rectangle(corner_radius, corner_radius, width - 2 * corner_radius, height - 2 * corner_radius)
context.set_source_rgb(0, 0, 0)
context.stroke()

# Draw the separator line
context.set_line_width(5)
context.set_source_rgb(0, 0, 0)  # Black color for the line
context.move_to(width / 2, height * 0.15)
context.line_to(width / 2, height * 0.85)
context.stroke()

# Draw the two dots on the left side
dot_radius = 5
context.set_source_rgb(0, 0, 0)

# Top dot
context.arc(width * 0.3, height * 0.35, dot_radius, 0, 2 * 3.1416)
context.fill()

# Bottom dot
context.arc(width * 0.3, height * 0.65, dot_radius, 0, 2 * 3.1416)
context.fill()

# Finish and save the SVG file
surface.finish()
print("SVG icon created as 'collapse.svg'")


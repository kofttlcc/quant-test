from core.frame_composer import (
    create_gradient_background,  # Gradient backgrounds
    draw_emoji_enhanced,         # Emoji with optional shadow
    draw_circle_with_shadow,     # Shapes with depth
    draw_star                    # 5-pointed stars
)

# Gradient background
frame = create_gradient_background(480, 480, top_color, bottom_color)

# Emoji with shadow
draw_emoji_enhanced(frame, '🎉', position=(200, 200), size=80, shadow=True)
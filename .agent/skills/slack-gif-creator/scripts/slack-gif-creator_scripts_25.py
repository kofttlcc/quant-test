from templates.shake import create_shake_animation

# Create shake animation
shake_frames = create_shake_animation(
    object_type='emoji',
    object_data={'emoji': '😰', 'size': 70},
    num_frames=20,
    shake_intensity=12
)

# Create moving element that triggers the shake
builder = GIFBuilder(480, 480, 20)
for i in range(40):
    t = i / 39

    if i < 20:
        # Before trigger - use blank frame with moving object
        frame = create_blank_frame(480, 480, (255, 255, 255))
        x = interpolate(50, 300, t * 2, 'linear')
        draw_emoji_enhanced(frame, '🚗', position=(int(x), 300), size=60)
        draw_emoji_enhanced(frame, '😰', position=(350, 200), size=70)
    else:
        # After trigger - use shake frame
        frame = shake_frames[i - 20]
        # Add the car in final position
        draw_emoji_enhanced(frame, '🚗', position=(300, 300), size=60)

    builder.add_frame(frame)

builder.save('scare.gif')
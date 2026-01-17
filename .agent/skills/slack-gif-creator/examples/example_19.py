# Example: Bounce + shake for impact
for i in range(num_frames):
    frame = create_blank_frame(480, 480, bg_color)

    # Bounce motion
    t_bounce = i / (num_frames - 1)
    y = interpolate(start_y, ground_y, t_bounce, 'bounce_out')

    # Add shake on impact (when y reaches ground)
    if y >= ground_y - 5:
        shake_x = math.sin(i * 2) * 10
        x = center_x + shake_x
    else:
        x = center_x

    draw_emoji(frame, '⚽', (x, y), size=60)
    builder.add_frame(frame)
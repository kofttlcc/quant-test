from templates.zoom import create_zoom_animation, create_explosion_zoom

# Zoom in dramatically
frames = create_zoom_animation(
    zoom_type='in',
    scale_range=(0.1, 2.0),
    add_motion_blur=True
)

# Zoom out
frames = create_zoom_animation(zoom_type='out')

# Explosion zoom
frames = create_explosion_zoom(emoji='💥')
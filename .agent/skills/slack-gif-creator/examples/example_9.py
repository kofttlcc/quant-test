from templates.pulse import create_pulse_animation, create_attention_pulse

# Smooth pulse
frames = create_pulse_animation(
    object_data={'emoji': '❤️', 'size': 100},
    pulse_type='smooth',
    scale_range=(0.8, 1.2)
)

# Heartbeat (double-pump)
frames = create_pulse_animation(pulse_type='heartbeat')

# Attention pulse for emoji GIFs
frames = create_attention_pulse(emoji='⚠️', num_frames=20)
from templates.wiggle import create_wiggle_animation, create_excited_wiggle

# Jello wobble
frames = create_wiggle_animation(
    wiggle_type='jello',
    intensity=1.0,
    cycles=2
)

# Wave motion
frames = create_wiggle_animation(wiggle_type='wave')

# Excited wiggle for emoji GIFs
frames = create_excited_wiggle(emoji='🎉')
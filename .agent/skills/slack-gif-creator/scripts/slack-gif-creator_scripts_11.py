from templates.explode import create_explode_animation, create_particle_burst

# Burst explosion
frames = create_explode_animation(
    explode_type='burst',
    num_pieces=25
)

# Shatter effect
frames = create_explode_animation(explode_type='shatter')

# Dissolve into particles
frames = create_explode_animation(explode_type='dissolve')

# Particle burst
frames = create_particle_burst(particle_count=30)
from templates.morph import create_morph_animation, create_reaction_morph

# Crossfade morph
frames = create_morph_animation(
    object1_data={'emoji': '😊', 'size': 100},
    object2_data={'emoji': '😂', 'size': 100},
    morph_type='crossfade'
)

# Scale morph (shrink while other grows)
frames = create_morph_animation(morph_type='scale')

# Spin morph (3D flip-like)
frames = create_morph_animation(morph_type='spin_morph')
from core.easing import interpolate

# Object falling (accelerates)
y = interpolate(start=0, end=400, t=progress, easing='ease_in')

# Object landing (decelerates)
y = interpolate(start=0, end=400, t=progress, easing='ease_out')

# Bouncing
y = interpolate(start=0, end=400, t=progress, easing='bounce_out')

# Overshoot (elastic)
scale = interpolate(start=0.5, end=1.0, t=progress, easing='elastic_out')
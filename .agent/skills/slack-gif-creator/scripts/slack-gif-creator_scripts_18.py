from core.gif_builder import GIFBuilder

# Create builder with your chosen settings
builder = GIFBuilder(width=480, height=480, fps=20)

# Add frames (however you created them)
for frame in my_frames:
    builder.add_frame(frame)

# Save with optimization
builder.save('output.gif',
             num_colors=128,
             optimize_for_emoji=False)
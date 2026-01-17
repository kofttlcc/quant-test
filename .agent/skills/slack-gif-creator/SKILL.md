---
name: slack-gif-creator
description: >-
  Toolkit for creating animated GIFs optimized for Slack, with validators for
  size constraints and composable animation primitives. This skill applies when
  users request animated GIFs or emoji animations for Slack from descriptions
  like "make me a GIF for Slack of X doing Y".
trigger: when_needed
language: zh-TW
adapted_from: openskills/slack-gif-creator
version: 1.0.0-antigravity
original_license: Complete terms in LICENSE.txt
---
# SLACK-GIF-CREATOR 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/slack-gif-creator  
> **語言**: 繁體中文

## 概述

Toolkit for creating animated GIFs optimized for Slack, with validators for size constraints and composable animation primitives. This skill applies when users request animated GIFs or emoji animations for Slack from descriptions like "make me a GIF for Slack of X doing Y".

---


# Slack GIF Creator - Flexible Toolkit

A toolkit for creating animated GIFs optimized for Slack. Provides validators for Slack's constraints, composable animation primitives, and optional helper utilities. **Apply these tools however needed to achieve the creative vision.**

## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---

## Slack's 需求

Slack has specific requirements for GIFs based on their use:

**Message GIFs:**
- Max size: ~2MB
- Optimal dimensions: 480x480
- Typical FPS: 15-20
- Color limit: 128-256
- Duration: 2-5s

**Emoji GIFs:**
- Max size: 64KB (strict limit)
- Optimal dimensions: 128x128
- Typical FPS: 10-12
- Color limit: 32-48
- Duration: 1-2s

**Emoji GIFs are challenging** - the 64KB limit is strict. Strategies that help:
- Limit to 10-15 frames total
- Use 32-48 colors maximum
- Keep designs simple
- Avoid gradients
- Validate file size frequently

## Toolkit Structure

This skill provides three types of tools:

1. **Validators** - Check if a GIF meets Slack's requirements
2. **Animation Primitives** - Composable building blocks for motion (shake, bounce, move, kaleidoscope)
3. **Helper Utilities** - Optional functions for common needs (text, colors, effects)

**Complete creative freedom is available in how these tools are applied.**

## Core Validators

To ensure a GIF meets Slack's constraints, use these validators:


詳細內容請參閱：[example_3.py](examples/example_3.py)


**File size validator**:
```python
from core.validators import check_slack_size

# Check if GIF meets size limits
passes, info = check_slack_size('emoji.gif', is_emoji=True)
# Returns: (True/False, dict with size details)

詳細內容請參閱：[example_4.txt](examples/example_4.txt)


**Complete validation**:

詳細內容請參閱：[example_5.py](examples/example_5.py)


## Animation Primitives

These are composable building blocks for motion. Apply these to any object in any combination:

### Shake

詳細內容請參閱：[example_6.py](examples/example_6.py)


### Bounce

詳細內容請參閱：[example_7.py](examples/example_7.py)


### Spin / Rotate

詳細內容請參閱：[example_8.py](examples/example_8.py)


### Pulse / Heartbeat

詳細內容請參閱：[example_9.py](examples/example_9.py)


### Fade

詳細內容請參閱：[example_10.py](examples/example_10.py)


### Zoom

詳細內容請參閱：[example_11.py](examples/example_11.py)


### Explode / Shatter

詳細內容請參閱：[example_12.py](examples/example_12.py)


### Wiggle / Jiggle

詳細內容請參閱：[example_13.py](examples/example_13.py)


### Slide

詳細內容請參閱：[example_14.py](examples/example_14.py)


### Flip

詳細內容請參閱：[example_15.py](examples/example_15.py)


### Morph / Transform

詳細內容請參閱：[example_16.py](examples/example_16.py)


### Move Effect

詳細內容請參閱：[example_17.py](examples/example_17.py)


### Kaleidoscope Effect

詳細內容請參閱：[example_18.py](examples/example_18.py)


**To compose primitives freely, follow these patterns:**

詳細內容請參閱：[example_19.py](examples/example_19.py)


## Helper Utilities

These are optional helpers for common needs. **Use, modify, or replace these with custom implementations as needed.**

### GIF Builder (Assembly & Optimization)


詳細內容請參閱：[example_20.py](examples/example_20.py)


Key features:
- Automatic color quantization
- Duplicate frame removal
- Size warnings for Slack limits
- Emoji mode (aggressive optimization)

### Text Rendering

For small GIFs like emojis, text readability is challenging. A common solution involves adding outlines:


詳細內容請參閱：[example_21.py](examples/example_21.py)


To implement custom text rendering, use PIL's `ImageDraw.text()` which works fine for larger GIFs.

### Color Management

Professional-looking GIFs often use cohesive color palettes:


詳細內容請參閱：[example_22.py](examples/example_22.py)


To work with colors directly, use RGB tuples - whatever works for the use case.

### Visual Effects

Optional effects for impact moments:


詳細內容請參閱：[example_23.py](examples/example_23.py)


### Easing Functions

Smooth motion uses easing instead of linear interpolation:


詳細內容請參閱：[example_24.py](examples/example_24.py)


Available easings: `linear`, `ease_in`, `ease_out`, `ease_in_out`, `bounce_out`, `elastic_out`, `back_out` (overshoot), and more in `core/easing.py`.

### Frame Composition

Basic drawing utilities if you need them:


詳細內容請參閱：[example_25.py](examples/example_25.py)


## Optimization Strategies

When your GIF is too large:

**For Message GIFs (>2MB):**
1. Reduce frames (lower FPS or shorter duration)
2. Reduce colors (128 → 64 colors)
3. Reduce dimensions (480x480 → 320x320)
4. Enable duplicate frame removal

**For Emoji GIFs (>64KB) - be aggressive:**
1. Limit to 10-12 frames total
2. Use 32-40 colors maximum
3. Avoid gradients (solid colors compress better)
4. Simplify design (fewer elements)
5. Use `optimize_for_emoji=True` in save method

## Example Composition Patterns

### Simple Reaction (Pulsing)

詳細內容請參閱：[example_26.py](examples/example_26.py)


### Action with Impact (Bounce + Flash)

詳細內容請參閱：[example_27.py](examples/example_27.py)


### Combining Primitives (Move + Shake)

詳細內容請參閱：[example_28.py](examples/example_28.py)


## Philosophy

This toolkit provides building blocks, not rigid recipes. To work with a GIF request:

1. **Understand the creative vision** - What should happen? What's the mood?
2. **Design the animation** - Break it into phases (anticipation, action, reaction)
3. **Apply primitives as needed** - Shake, bounce, move, effects - mix freely
4. **Validate constraints** - Check file size, especially for emoji GIFs
5. **Iterate if needed** - Reduce frames/colors if over size limits

**The goal is creative freedom within Slack's technical constraints.**

## Dependencies

To use this toolkit, install these dependencies only if they aren't already present:

```bash
pip install pillow imageio numpy
```


---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 `skills/_base/coding_style.md` 編碼規範
- 與 `skills/_base/architecture.md` 架構模式一致
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

可搭配以下技能使用：
- `systematic-debugging` - 系統化除錯
- `verification-before-completion` - 完成前驗證
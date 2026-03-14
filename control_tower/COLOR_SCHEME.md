# Green Loop Control Tower - Color Scheme

## Theme: Sustainability & Nature

The app uses an earth-toned, sustainability-focused color palette that reflects the recycling and environmental mission.

## Primary Colors

### Green (Sustainability/Progress)
- **Dark Green** `#2E7D32` - Primary brand color, borders, headers
- **Forest Green** `#1B5E20` - Text headers, strong emphasis
- **Light Green** `#7CB342` - Secondary actions, moderate status
- **Pale Green** `#A5D6A7` - Subtle accents, dividers

### Earth Tones (Nature/Warning)
- **Olive/Gold** `#C0A04C` - Warning state (underserved)
- **Olive Green** `#827717` - Warning text
- **Brown** `#8D6E63` - Critical state (needs attention)
- **Dark Brown** `#5D4037` - Critical text

### Neutrals
- **White** `#FFFFFF` / `rgba(255, 255, 255, 0.98)` - Backgrounds, cards
- **Light Gray** (CartoDB Positron basemap) - Map background

## Coverage Status Colors

| Status | Color | Hex Code | Usage |
|--------|-------|----------|-------|
| Well-served (<300m) | Dark Green | `#2E7D32` | Estate markers, legend |
| Moderate (300-500m) | Light Green | `#7CB342` | Estate markers, legend |
| Underserved (500-800m) | Olive/Gold | `#C0A04C` | Estate markers, legend |
| Critical (>800m) | Brown | `#8D6E63` | Estate markers, legend |

## UI Elements

### Map Legend
- **Background**: `rgba(255, 255, 255, 0.98)` - Semi-transparent white
- **Border**: `2px solid #2E7D32` - Dark green
- **Title**: `#1B5E20` - Forest green
- **Divider**: `2px solid #A5D6A7` - Pale green
- **Shadow**: `0 4px 12px rgba(46, 125, 50, 0.2)` - Soft green glow

### Map Title Boxes
- **Background**: `rgba(255, 255, 255, 0.98)`
- **Border**: `2px solid #2E7D32`
- **Title Text**: `#1B5E20`
- **Shadow**: `0 3px 8px rgba(46, 125, 50, 0.2)`

### Hub Icons
- **Color**: `green` (Folium green)
- **Icon**: `recycle` (Font Awesome)

## Design Principles

1. **Green = Good** - Darker greens indicate better service
2. **Earth Tones = Warning** - Natural browns/golds for areas needing improvement
3. **No Red** - Avoid aggressive red; use warm earth tones instead
4. **Soft Shadows** - Green-tinted shadows for cohesion
5. **High Contrast** - Dark text on white backgrounds for readability

## Accessibility

- All text meets WCAG AA contrast requirements
- Color-blind friendly (green-brown scale avoids red-green confusion)
- Consistent color meanings across all pages

## Examples

### Well-Served Estate
```
Marker: #2E7D32 (Dark Green)
Text: "Well-served" in #2E7D32
```

### Underserved Estate
```
Marker: #C0A04C (Olive/Gold)
Text: "Underserved" in #827717
```

### Critical Estate
```
Marker: #8D6E63 (Brown)
Text: "Critical" in #5D4037
```

## Changed From

Previous color scheme (removed):
- Orange `#F59E0B`
- Red `#EF4444`
- Dark Red `#991B1B`
- Black borders `#333`

Reason: Too harsh, not aligned with sustainability theme

## New Scheme Benefits

- More cohesive with recycling/sustainability mission
- Softer, more approachable aesthetic
- Earth-toned palette feels natural and calming
- Green branding reinforces environmental focus
- Better visual hierarchy with consistent green accents

# Capture Sound

The extension plays a subtle sound when capturing to provide audio feedback.

## Quick Setup

### Option 1: Use a Free Sound (Recommended)

Download a short, subtle sound:

**Good sources:**
- **Freesound.org**: https://freesound.org/search/?q=camera+shutter
- **Mixkit**: https://mixkit.co/free-sound-effects/click/
- **Zapsplat**: https://www.zapsplat.com/sound-effect-category/camera-shutter/

**Requirements:**
- Format: MP3
- Length: < 1 second
- Volume: Quiet/subtle
- Name: `capture.mp3`

**Recommendations:**
- Camera shutter sound
- Soft click
- Gentle beep
- Subtle notification tone

Save as `synapse-extension/capture.mp3`

### Option 2: Skip Sound

The extension works perfectly without sound. The visual feedback (flash + toast) is enough.

To disable sound checking:
1. Leave `capture.mp3` missing
2. The extension will silently skip sound playback
3. Everything else works normally

## Testing

After adding the sound:

1. Reload the extension
2. Open any webpage
3. Press `Ctrl+Shift+S`
4. You should hear a brief, subtle sound
5. Adjust your volume if needed

## Troubleshooting

### Sound not playing?

**Common causes:**
- Browser blocked autoplay (normal, not a problem)
- File path incorrect (must be in root of extension folder)
- File format not MP3
- Sound too quiet

**Check:**
```javascript
// Open extension service worker console
// chrome://extensions/ -> Synapse -> service worker
// Should see no errors about capture.mp3
```

### Sound too loud/quiet?

Edit `content.js`, line with `audio.volume`:

```javascript
audio.volume = 0.3; // Change from 0.0 (silent) to 1.0 (full)
```

Recommended: 0.2 - 0.4 for subtle feedback

## Example Sounds

Here are some good free options:

1. **Camera Shutter** - Classic capture sound
   - https://freesound.org/people/thecheeseman/sounds/44428/

2. **Soft Click** - Minimal and quick
   - https://freesound.org/people/kwahmah_02/sounds/256116/

3. **Gentle Beep** - Subtle notification
   - https://freesound.org/people/Bertrof/sounds/351565/

**Note:** Always check license before downloading!

## For Developers

The sound is played in `content.js`:

```javascript
function playSound() {
  const audio = new Audio(chrome.runtime.getURL('capture.mp3'));
  audio.volume = 0.3;
  audio.play().catch(() => {
    // Silently fail if blocked
  });
}
```

The file is registered in `manifest.json` as a web-accessible resource.

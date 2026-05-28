# Historial de Commits - dmidiplayer & wps-dicts

This document compiles the summaries of changes provided during the session and the `git commit` commands generated following the established conventions (Conventional Commits, max 50 chars in subject, max 72 chars in body).

---

## 1. Rhythm View Implementation

**Texto Original:**
> We got the Rhythm view over the line.
> In [app.py]..., I added an embedded `RhythmView` panel that shows: current meter, current bar, current beat, current BPM, a live beat strip... It updates from the same playback position flow... I also added a `View -> Rhythm` toggle...
> To support that cleanly, [sequence.py]... now has `time_signature_at_tick()`...
> Tests in [test_app_playlist.py]... now cover: rhythm action existence, toggling... rhythm panel updates...
> I also updated [Roadmap.md]... to mark these complete...
> Verification is clean: compileall passed, full unittest suite passed: 106 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add embedded Rhythm view with playback sync" \
  -m "- Add RhythmView panel showing meter, bar, beat, BPM, and strip" \
  -m "- Sync updates with playback position, tempo changes, and seeks" \
  -m "- Add View > Rhythm toggle for show/hide control" \
  -m "- Implement time_signature_at_tick() in sequence.py for UI queries" \
  -m "- Add tests for rhythm action, toggling, and live updates" \
  -m "- Update Roadmap.md to mark rhythm view items complete" \
  -m "- Validation: compileall OK, 106 tests pass, offscreen verified"
```

---

## 2. Preferences: Solo Reduction & GM Reset

**Texto Original:**
> We landed another useful preferences slice with real playback behavior behind it.
> In [settings.py]..., I added persisted General-tab settings for: `solo_volume_reduction` with a default of `50%`, `midi_reset_before_playback` with a default of `False`...
> In [app.py]..., the Preferences dialog’s `General` tab now includes: `Solo volume reduction`, `Send GM reset before playback`...
> In [player.py]..., I added actual GM reset behavior: when that preference is enabled, playback sends the standard GM reset SysEx...
> Tests were expanded across: test_settings.py, test_sequence_player.py, test_app_playlist.py...
> I also updated [Roadmap.md]... to mark these General-tab items complete...
> Verification is clean: ... 110 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add solo reduction and GM reset prefs" \
  -m "- Persist solo_volume_reduction (default 50%) and midi_reset" \
  -m "- Add General tab controls for both settings in Preferences dialog" \
  -m "- Send GM reset SysEx before playback when enabled in player.py" \
  -m "- Add tests for persistence, clamping, and reset behavior" \
  -m "- Update Roadmap.md to mark General tab items complete" \
  -m "- Validation: compileall OK, 110 tests pass, offscreen verified"
```

---

## 3. User Guide Implementation

**Texto Original:**
> We added real user-facing help for the PyQt6 app and exposed it from the interface.
> In [app.py]..., I added: a new `Help -> User Guide` action, shared localized document lookup for help files, a direct user-guide dialog...
> I created two new guide files: dmidiplayer/docs/en/pyqt6-user-guide.md, dmidiplayer/docs/es/pyqt6-user-guide.md...
> I also updated the local help indexes...
> Tests in [test_app_playlist.py]... now cover: `User Guide` action existence, localized guide-path resolution...
> And I updated [Roadmap.md]... to mark the local-help/app-help pieces as done.
> Verification is clean: ... 111 tests OK...

**Comando Generado:**
```bash
git commit -m "docs(app): add localized PyQt6 user guide" \
  -m "- Add Help > User Guide action with shared localized lookup" \
  -m "- Create comprehensive EN/ES guides for UI controls and menus" \
  -m "- Update local help indexes to reference new user guide" \
  -m "- Add tests for action existence and path resolution" \
  -m "- Update Roadmap.md to mark local help items complete" \
  -m "- Validation: compileall OK, 111 tests pass, offscreen verified"
```

---

## 4. Channels View (Initial)

**Texto Original:**
> We moved the first real Channels view into the PyQt6 app.
> In [app.py]..., I added a `View -> Channels` action and a new non-modal `ChannelsDialog` that shows one row per used MIDI channel with: channel number, editable label, live level meter...
> In [sequence.py]..., I added `used_channels()` so the UI can ask the sequence model which MIDI channels are actually present...
> I also updated the user guide files...
> Tests in [test_app_playlist.py]... now cover: `Channels` action existence, opening the Channels dialog, listing used channels...
> And [Roadmap.md]... is now updated to mark these done...
> Verification is clean: ... 114 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add Channels view with live level meters" \
  -m "- Add View > Channels action and non-modal ChannelsDialog" \
  -m "- Display used channels with editable labels and activity meters" \
  -m "- Sync meter updates with playback events; clear on stop/seek" \
  -m "- Implement used_channels() in sequence.py for UI queries" \
  -m "- Update user guides (EN/ES) to document the new Channels window" \
  -m "- Add tests for dialog lifecycle, listing, and meter updates" \
  -m "- Update Roadmap.md to mark Channels view items complete" \
  -m "- Validation: compileall OK, 114 tests pass, offscreen verified"
```

---

## 5. Channels View: Mute & Solo

**Texto Original:**
> We pushed the Channels view from read-only into something genuinely interactive.
> In [player.py]..., I added per-channel playback controls: muted channel tracking, solo channel tracking, solo reduction percentage support...
> In [app.py]..., the `Channels` window now has real `Mute` and `Solo` checkboxes per row...
> I updated the user guides too...
> Tests were expanded in: test_sequence_player.py, test_app_playlist.py... They now cover: muted-channel note silencing, solo reduction...
> And [Roadmap.md]... is updated to mark these channel-view items complete...
> Verification is clean: ... 119 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add interactive Mute/Solo to Channels view" \
  -m "- Implement per-channel mute/solo tracking in player.py" \
  -m "- Filter playback events based on channel state" \
  -m "- Apply solo reduction preference to non-soloed channels" \
  -m "- Add Mute/Solo checkboxes to ChannelsDialog in app.py" \
  -m "- Update user guides (EN/ES) with new control documentation" \
  -m "- Add tests for silencing, reduction, and UI wiring" \
  -m "- Update Roadmap.md to mark mute/solo items complete" \
  -m "- Validation: compileall OK, 119 tests pass, offscreen verified"
```

---

## 6. Channels View: Volume Sliders

**Texto Original:**
> We kept the Channels work moving and added per-channel volume.
> In [player.py]..., I added per-channel volume percentages and applied them in playback before the global volume scaling...
> In [app.py]..., the `Channels` window now has a `Volume` slider per row... Moving the slider updates the player immediately...
> I also fixed the channel dialog’s level-reset bookkeeping...
> Tests were extended in: test_sequence_player.py, test_app_playlist.py... They now cover: per-channel volume scaling... immediate CC7 send...
> I updated the user guides too... And [Roadmap.md]... now marks `Volume slider per channel` complete.
> Verification is clean: ... 122 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add per-channel volume sliders" \
  -m "- Implement per-channel volume scaling before global volume" \
  -m "- Send immediate CC7 updates on slider change" \
  -m "- Add Volume slider to ChannelsDialog alongside Mute/Solo" \
  -m "- Fix level meter index after previous UI expansion" \
  -m "- Update user guides (EN/ES) with new volume control docs" \
  -m "- Add tests for scaling order, CC7 sends, and UI wiring" \
  -m "- Update Roadmap.md to mark volume slider item complete" \
  -m "- Validation: compileall OK, 122 tests pass, offscreen verified"
```

---

## 7. Channels View: Program Control

**Texto Original:**
> We kept the Channels view moving and added patch/program control.
> In [app.py]..., the `Channels` window now has a `Program` spinbox per row. It’s initialized from the first program-change event...
> In [player.py]..., I added per-channel program overrides. Those overrides now do two useful things: send an immediate `program_change`... replace later file-sent `program_change` events...
> To support sensible initial values, [sequence.py]... now exposes `initial_programs()`.
> Tests were expanded... They now cover: program override rewriting file program changes...
> I also updated the user guides... And [Roadmap.md]... now marks the basic patch/program selector complete...
> Verification is clean: ... 125 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add per-channel program control" \
  -m "- Add Program spinbox to ChannelsDialog with immediate CC send" \
  -m "- Implement program overrides that replace file events during playback" \
  -m "- Expose initial_programs() in sequence.py for UI initialization" \
  -m "- Update user guides (EN/ES) with new program control docs" \
  -m "- Add tests for overrides, immediate sends, and UI wiring" \
  -m "- Update Roadmap.md to mark basic patch selector complete" \
  -m "- Validation: compileall OK, 125 tests pass, offscreen verified"
```

---

## 8. Channels View: Patch Lock

**Texto Original:**
> We carried the Channels view one step further and added patch lock.
> In [player.py]..., I added per-channel lock state. Locked channels now suppress file-sent `program_change` events...
> In [app.py]..., the `Channels` window now has a `Lock` checkbox column beside `Program`...
> Tests were expanded... They now cover: locked channel suppressing file program changes... lock checkbox wiring...
> I also updated the user guides... And [Roadmap.md]... now marks patch lock complete.
> Verification is clean: ... 128 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add patch lock to Channels view" \
  -m "- Implement per-channel lock state in player.py" \
  -m "- Suppress file program changes for locked channels" \
  -m "- Add Lock checkbox column to ChannelsDialog" \
  -m "- Update user guides (EN/ES) with new lock control docs" \
  -m "- Add tests for lock behavior and UI wiring" \
  -m "- Update Roadmap.md to mark patch lock item complete" \
  -m "- Validation: compileall OK, 128 tests pass, offscreen verified"
```

---

## 9. Channels View: GM Names

**Texto Original:**
> We made the channel patch selector much nicer to use.
> In [app.py]..., I replaced the raw numeric `Program` spinbox with a `QComboBox` showing General MIDI instrument names...
> I added a small General MIDI name table plus `gm_program_label()`...
> Tests in [test_app_playlist.py]... were updated to verify: the program cell is now a combo box...
> I also updated: [Roadmap.md]... [dmidiplayer/docs/en/pyqt6-user-guide.md]...
> Verification is clean: ... 128 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): use GM names for channel program selector" \
  -m "- Replace numeric spinbox with QComboBox showing GM instrument names" \
  -m "- Add internal GM name table and gm_program_label() helper" \
  -m "- Maintain 0-127 program value mapping underneath UI labels" \
  -m "- Update tests to verify combo box behavior and display text" \
  -m "- Update user guides (EN/ES) to reflect new selector UI" \
  -m "- Update Roadmap.md to mark GM name selector complete" \
  -m "- Validation: compileall OK, 128 tests pass, offscreen verified"
```

---

## 10. Lyrics Window (Initial)

**Texto Original:**
> We moved the first real Lyrics window into the PyQt6 port.
> In [app.py]..., I added `View -> Lyrics` and a non-modal `LyricsDialog` that shows MIDI/KAR text events... It already supports filtering by text type...
> To support that cleanly, [sequence.py]... now exposes `text_events()`...
> I also updated the user guides... and marked the new completed lyrics items in [Roadmap.md]...
> Test coverage for the new window and filters is in [test_app_playlist.py]...
> Verification is clean: ... 131 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add Lyrics window with text type filtering" \
  -m "- Add View > Lyrics action and non-modal LyricsDialog" \
  -m "- Display MIDI/KAR text events with filter for type (Lyrics, Text, etc.)" \
  -m "- Expose text_events() in sequence.py for UI queries" \
  -m "- Update user guides (EN/ES) to document the new Lyrics window" \
  -m "- Add tests for dialog lifecycle, event listing, and filtering" \
  -m "- Update Roadmap.md to mark initial lyrics view items complete" \
  -m "- Validation: compileall OK, 131 tests pass, offscreen verified"
```

---

## 11. Lyrics Window: Track Filtering

**Texto Original:**
> We kept the Lyrics view moving and made it track-aware.
> In [drumstick/drumstick_py/file.py], `TextEvent` now remembers its source track...
> Then in [app.py]..., the `Lyrics` window gained a `Track:` filter with `All tracks` plus one entry per text-bearing track, and it now auto-selects the track with the most text events...
> I updated [Roadmap.md]... refreshed the user guides... and added coverage in [test_smf_parser.py] and [test_app_playlist.py]...
> Verification is clean: ... 134 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add track filtering to Lyrics window" \
  -m "- Preserve source track info in TextEvent via drumstick_py/file.py" \
  -m "- Add Track filter with auto-selection of most text-heavy track" \
  -m "- Prefix lines with track number in All tracks view for clarity" \
  -m "- Update user guides (EN/ES) with new filtering documentation" \
  -m "- Add tests for track metadata, selection, and filtering logic" \
  -m "- Update Roadmap.md to mark track filtering items complete" \
  -m "- Validation: compileall OK, 134 tests pass, offscreen verified"
```

---

## 12. Lyrics Window: Copy & Font

**Texto Original:**
> We gave the Lyrics window a bit more real-world usefulness.
> In [app.py]..., the `LyricsDialog` now has `Copy` and `Font` buttons. `Copy` puts the currently filtered text into the clipboard... `Font` opens a real font chooser...
> I added tests in [test_app_playlist.py]... and updated [Roadmap.md]... The user guides were updated too...
> Verification is clean: ... 136 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add Copy and Font controls to Lyrics window" \
  -m "- Add Copy button to export filtered text to clipboard" \
  -m "- Add Font button for real-time lyrics pane styling" \
  -m "- Update user guides (EN/ES) with new control documentation" \
  -m "- Add tests for clipboard content and font dialog behavior" \
  -m "- Update Roadmap.md to mark copy/font items complete" \
  -m "- Validation: compileall OK, 136 tests pass, offscreen verified"
```

---

## 13. About Dialog Enhancement

**Texto Original:**
> Yes, that wording is fine, and I’ve now wired the idea into the app.
> In [app.py]..., `Help > About` now includes: original C++ credit... Python/PyQt6 port credit... clickable author names using `mailto:` links... GPL notice... a short “Technologies used in this port” section...
> I also updated the help-guide text... and expanded [test_app_playlist.py]...
> Verification is clean: ... 136 tests OK...

**Comando Generado:**
```bash
git commit -m "docs(app): enhance About dialog with credits and tech" \
  -m "- Add C++ and Python/PyQt6 port credits with clickable mailto links" \
  -m "- Hide emails via hover text while keeping names visible" \
  -m "- Include GPL notice and 'Technologies used' section" \
  -m "- Update user guides (EN/ES) to reflect new About content" \
  -m "- Add tests for credit presence, links, and technology list" \
  -m "- Validation: compileall OK, 136 tests pass, offscreen verified"
```

---

## 14. Lyrics Window: Save & Encoding

**Texto Original:**
> We pushed the Lyrics window a little further into “actually useful.”
> In [app.py]..., the dialog now has: an `Encoding` selector with `UTF-8`, `Latin-1`, and `CP1252`, a `Save` button that writes exactly the current filtered text to a file...
> I covered that in [test_app_playlist.py]... with checks for: saving the current filtered lyrics text... honoring a non-default encoding...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 138 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add encoding selector and save to Lyrics window" \
  -m "- Add Encoding dropdown (UTF-8, Latin-1, CP1252) for text display" \
  -m "- Implement Save button to export filtered text with selected encoding" \
  -m "- Emit textSaved signal for status bar confirmation feedback" \
  -m "- Update user guides (EN/ES) with new export documentation" \
  -m "- Add tests for saving, encoding handling, and UI feedback" \
  -m "- Update Roadmap.md to mark lyrics export item complete" \
  -m "- Validation: compileall OK, 138 tests pass, offscreen verified"
```

---

## 15. Lyrics Window: Fullscreen

**Texto Original:**
> We finished another tidy Lyrics-window slice: fullscreen mode.
> In [app.py]..., the dialog now has a `Fullscreen` button that toggles between normal and fullscreen display, and `Esc` exits fullscreen cleanly...
> I added coverage in [test_app_playlist.py]... updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 140 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add fullscreen mode to Lyrics window" \
  -m "- Add Fullscreen/Window toggle button with dynamic label" \
  -m "- Support Esc key to exit fullscreen cleanly" \
  -m "- Update user guides (EN/ES) with new fullscreen documentation" \
  -m "- Add tests for toggle behavior and Esc exit path" \
  -m "- Update Roadmap.md to mark fullscreen item complete" \
  -m "- Validation: compileall OK, 140 tests pass, offscreen verified"
```

---

## 16. Lyrics Window: Print

**Texto Original:**
> We moved the Lyrics window another step forward: it can print now.
> In [app.py]..., I added a `Print` button that sends the currently filtered text through Qt’s standard print dialog...
> Tests in [test_app_playlist.py]... now cover: accepted print flow... cancelled print dialog...
> I updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 142 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add print support to Lyrics window" \
  -m "- Add Print button using Qt standard print dialog for filtered text" \
  -m "- Emit textPrinted signal for status bar confirmation on success" \
  -m "- Update user guides (EN/ES) with new printing documentation" \
  -m "- Add tests for accepted/cancelled print flows and feedback" \
  -m "- Update Roadmap.md to mark print lyrics item complete" \
  -m "- Validation: compileall OK, 142 tests pass, offscreen verified"
```

---

## 17. Lyrics Window: Auto-Detection Encoding

**Texto Original:**
> We pushed the Lyrics window through the encoding milestone.
> In [drumstick/drumstick_py/file.py], text events now keep their raw bytes and decode through a shared helper... try `UTF-8`, then prefer `CP1252`... otherwise fall back to `Latin-1`.
> In [app.py]..., the Lyrics window’s `Encoding` selector now controls both display decoding and save behavior: `Auto`, `UTF-8`, `Latin-1`, `CP1252`...
> I added coverage in [test_smf_parser.py] and [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 145 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add auto-detection and override for lyrics encoding" \
  -m "- Store raw bytes in TextEvent; decode via shared helper on demand" \
  -m "- Implement auto-detection: UTF-8 -> CP1252 heuristic -> Latin-1 fallback" \
  -m "- Add Auto option to Encoding selector in LyricsDialog" \
  -m "- Update save logic: Auto writes UTF-8, others use selected encoding" \
  -m "- Add tests for detection, manual override, and save behavior" \
  -m "- Update user guides (EN/ES) with new encoding documentation" \
  -m "- Update Roadmap.md to mark encoding detection item complete" \
  -m "- Validation: compileall OK, 145 tests pass, offscreen verified"
```

---

## 18. Lyrics Window: Highlighting

**Texto Original:**
> We landed the next lyrics milestone: live past/current/future highlighting during playback.
> In [app.py]..., the `LyricsDialog` now keeps the current playback tick, filters the visible events, and renders them as HTML with three states: past lines dimmed, current line emphasized, future lines clearly visible...
> I added a timed-lyrics fixture and coverage in [test_app_playlist.py]...
> I also updated the user guides... [Roadmap.md]... now marks `Highlight past/future lyrics with configurable colors` complete.
> Verification is clean: ... 146 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add live lyric highlighting during playback" \
  -m "- Sync LyricsDialog with playback tick for real-time updates" \
  -m "- Render HTML with distinct styles for past, current, and future lines" \
  -m "- Add timed-lyrics fixture and tests for state transitions" \
  -m "- Update user guides (EN/ES) with new highlighting documentation" \
  -m "- Update Roadmap.md to mark lyric highlighting item complete" \
  -m "- Validation: compileall OK, 146 tests pass, offscreen verified"
```

---

## 19. Roadmap & GUI Reference Process

**Texto Original:**
> Done. I updated [Roadmap.md]... so the new `Roadmap-GUI/` material is part of the ongoing port process...
> What I added: `Roadmap-GUI/dmidiplayer-GUI.md` to the “read this first” list, a new **GUI Reference Check** section... explicit references to screenshots... an always-active checklist requiring visual comparison...
> I also updated the roadmap date to `2026-05-07`.
> No code changed this round, just the roadmap/handoff process.

**Comando Generado:**
```bash
git commit -m "docs(roadmap): integrate GUI reference check process" \
  -m "- Add Roadmap-GUI/dmidiplayer-GUI.md to primary reading list" \
  -m "- Create GUI Reference Check section with visual comparison checklist" \
  -m "- Link key reference screenshots (Playlist, Lyrics, Channels, Piano)" \
  -m "- Require visual verification before marking windows complete" \
  -m "- Update roadmap date to 2026-05-07" \
  -m "- No code changes; documentation and process update only"
```

---

## 20. Lyric Track Priority Fix & Pianola Rules

**Texto Original:**
> Done, and this was a good correction.
> What changed: In [app.py]..., the `Lyrics` window now prefers the track that actually contains lyric meta events (`0x05`) when a file has lyrics. If there is no dedicated lyrics track, it still falls back to the track with the most text events.
> I added a regression test in [test_app_playlist.py]...
> I also updated [Roadmap.md]... so these rules are explicit: `Channels` should show only channels present... `Player Piano / Pianola` should show only tracks/channels that are actually present... `Lyrics And Karaoke` should prefer the lyrics track...
> And I updated the user guides...
> Verification is clean: ... 147 tests OK...

**Comando Generado:**
```bash
git commit -m "fix(app): prioritize lyric tracks in Lyrics window" \
  -m "- Prefer track with lyric meta events (0x05) over generic text" \
  -m "- Fallback to most text-heavy track if no dedicated lyrics exist" \
  -m "- Add regression test to lock in correct track selection logic" \
  -m "- Update Roadmap.md with explicit visibility rules for all views" \
  -m "- Update user guides (EN/ES) to clarify lyrics track priority" \
  -m "- Validation: compileall OK, 147 tests pass, offscreen verified"
```

*(Nota: Este commit se combinó posteriormente con los dos siguientes en un solo commit histórico, pero aquí se muestra individualmente como se generó en su momento).*

---

## 21. Pianola Tab Architecture Definition

**Texto Original:**
> Done. I added your tab rule directly to the `Player Piano / Pianola` section in [Roadmap.md]...
> - first tab opens by default
> - maximum 8 MIDI tracks per tab
> - tracks 9-16 go to a second tab
> - tracks beyond 16 go to a third tab
> - the user must be able to click the tab they need to view the relevant instruments/tracks

**Comando Generado:**
```bash
git commit -m "docs(roadmap): define tab architecture for Pianola view" \
  -m "- Specify default first tab and max 8 tracks per tab rule" \
  -m "- Define overflow logic: tracks 9-16 to tab 2, 17+ to tab 3" \
  -m "- Require clickable tabs for easy navigation of instruments" \
  -m "- Establish build contract before implementing Pianola window" \
  -m "- No code changes; documentation and architectural planning only"
```

---

## 22. Combined Commit (Roadmap + Lyrics Fix + Pianola Rules)

*(Este fue el resultado de combinar los commits 19, 20 y 21 en uno solo como solicitaste)*

**Comando Generado:**
```bash
git commit -m "docs(app): update roadmap rules and fix lyric track priority" \
  -m "- Integrate GUI reference check process with visual comparison checklist" \
  -m "- Link key reference screenshots (Playlist, Lyrics, Channels, Piano)" \
  -m "- Prefer lyric meta events (0x05) over generic text in Lyrics window" \
  -m "- Fallback to most text-heavy track if no dedicated lyrics exist" \
  -m "- Add regression test to lock in correct track selection logic" \
  -m "- Define Pianola tab architecture: max 8 tracks per tab with overflow" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new visibility rules" \
  -m "- Validation: compileall OK, 147 tests pass, offscreen verified"
```

---

## 23. Piano Player Window (Initial)

**Texto Original:**
> We landed the first real `Piano Player` window slice, and it follows the tab rule you asked for.
> In [sequence.py]..., I added `midi_tracks()` so the app can ask for only the tracks that actually contain MIDI channel events. Then in [app.py]..., I added: a new `View -> Piano Player` action, a `PianolaDialog`, tab splitting at 8 MIDI-bearing tracks per tab...
> So right now: only tracks that really contain MIDI are shown... first tab opens by default...
> I also updated [Roadmap.md]... and documented it in the user guides...
> Tests were expanded in [test_app_playlist.py]...
> Verification is clean: ... 151 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add Piano Player window with tabbed tracks" \
  -m "- Add View > Piano Player action and PianolaDialog class" \
  -m "- Implement midi_tracks() in sequence.py to filter active tracks" \
  -m "- Split tracks into tabs of 8 (1-8, 9-16, 17+) per roadmap rules" \
  -m "- Display per-track rows with labels and live PianoKeyboard widgets" \
  -m "- Route playback note updates to relevant track keyboards" \
  -m "- Clear state on stop/seek/load transitions for consistency" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new view docs" \
  -m "- Add tests for action, track filtering, tab splitting, and activity" \
  -m "- Validation: compileall OK, 151 tests pass, offscreen verified"
```

---

## 24. Piano Player: Richer Track Info

**Texto Original:**
> We refined the first `Piano Player` slice so it’s easier to use.
> In [sequence.py]..., I added `midi_track_infos()` so the UI can get: track number, MIDI-bearing channels, first track title/instrument-style meta label...
> Then in [app.py]..., each Pianola row now shows: a richer track heading like `Track 2 - Part 2`, a channel summary like `Channels: 2`...
> I updated [Roadmap.md]... and I refreshed the user guides... Tests in [test_app_playlist.py]... were expanded...
> Verification is clean: ... 151 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): enrich Pianola rows with track info" \
  -m "- Add midi_track_infos() to expose labels and channel data" \
  -m "- Display rich headings (e.g., 'Track 2 - Part 2') per row" \
  -m "- Show channel summary (e.g., 'Channels: 2') above keyboards" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new details" \
  -m "- Add tests for label rendering and channel summary accuracy" \
  -m "- Validation: compileall OK, 151 tests pass, offscreen verified"
```

---

## 25. Piano Player: Auto-Range Keyboards

**Texto Original:**
> We kept the Pianola window moving in a useful direction: each track keyboard now narrows itself to the notes that track actually uses.
> What changed: In [widgets.py]..., `PianoKeyboard` now supports a configurable note range. In [sequence.py]..., `midi_track_infos()` now includes per-track `min_note` and `max_note`. In [app.py]..., the Pianola row keyboards pick up that range...
> I also updated: [Roadmap.md]... [EN guide]... [ES guide]...
> Tests were expanded in [test_app_playlist.py]...
> Verification is clean: ... 152 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): auto-range Pianola keyboards to used notes" \
  -m "- Add configurable note range support to PianoKeyboard widget" \
  -m "- Expose min/max note per track via midi_track_infos() in sequence.py" \
  -m "- Initialize each Pianola row keyboard with its specific note range" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new behavior docs" \
  -m "- Add tests for per-track note range calculation and application" \
  -m "- Validation: compileall OK, 152 tests pass, offscreen verified"
```

---

## 26. PianoKeyboard: Black Keys

**Texto Original:**
> We improved the shared keyboard layer in a meaningful way: `PianoKeyboard` now supports black keys and a real configurable note range.
> In [widgets.py]..., I added: `visible_white_notes()`, `visible_black_notes()`, real black-key drawing on top of the white-key base...
> I also added a dedicated widget test file, [test_widgets.py]...
> And I updated: [Roadmap.md]... [EN guide]... [ES guide]...
> Verification is clean: ... 154 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add black keys and range support to PianoKeyboard" \
  -m "- Implement visible_white_notes() and visible_black_notes() helpers" \
  -m "- Render black keys on top of white-key base for realistic look" \
  -m "- Support range-aware rendering via existing set_note_range()" \
  -m "- Add test_widgets.py for note lists and MIDI-range clamping" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new widget docs" \
  -m "- Validation: compileall OK, 154 tests pass, offscreen verified"
```

---

## 27. Piano Player: Visibility Controls

**Texto Original:**
> We moved the Pianola window forward in a pretty useful way.
> In [app.py]..., the `Piano Player` dialog now has real per-track visibility controls: each track row gets a `Show` checkbox, `Show All` / `Hide All` buttons... hidden rows collapse just the keyboard area...
> While I was there, I also cleaned up a duplicate Pianola clear in slider seeking...
> I added coverage in [test_app_playlist.py]...
> I also updated [Roadmap.md]... and the user guides...
> Verification is clean: ... 157 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add per-track visibility controls to Pianola" \
  -m "- Add Show checkbox per track row with keyboard area collapsing" \
  -m "- Implement Show All / Hide All buttons for bulk visibility toggling" \
  -m "- Report visibility changes in main window status bar" \
  -m "- Fix duplicate Pianola clear on seek and ensure stop/pause cleanup" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new control docs" \
  -m "- Add tests for individual/bulk toggling and activity clearing" \
  -m "- Validation: compileall OK, 157 tests pass"
```

---

## 28. Piano Player: Fullscreen

**Texto Original:**
> We kept the Pianola window moving and knocked out fullscreen.
> In [app.py]..., the `Piano Player` dialog now has a `Fullscreen` toggle button, and `Esc` exits fullscreen cleanly. I used the same behavior pattern as the Lyrics window...
> I added coverage in [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 159 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add fullscreen mode to Piano Player window" \
  -m "- Add Fullscreen toggle button with Esc key exit support" \
  -m "- Reuse Lyrics window pattern for consistent app-wide behavior" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new docs" \
  -m "- Add tests for fullscreen toggle and Esc exit path" \
  -m "- Validation: compileall OK, 159 tests pass"
```

---

## 29. Piano Player: Range Modes

**Texto Original:**
> We kept the Pianola window moving and finished another roadmap item: range mode.
> In [app.py]..., the `Piano Player` dialog now has a `Range` selector with: `Exact`, `Used octaves`... `Exact` keeps the current tight per-track note span. `Used octaves` expands each track to full octave boundaries...
> I added coverage in [test_app_playlist.py]...
> I updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 160 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add range modes to Piano Player window" \
  -m "- Add Range selector with Exact and Used octaves options" \
  -m "- Expand keyboards to full octave boundaries in Used octaves mode" \
  -m "- Keep Exact mode as default for tight per-track note spans" \
  -m "- Show status bar confirmation when range mode changes" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new docs" \
  -m "- Add tests for range expansion logic and UI feedback" \
  -m "- Validation: compileall OK, 160 tests pass"
```

---

## 30. Piano Player: Velocity Tinting

**Texto Original:**
> We kept the Pianola work moving and landed velocity tinting.
> In [widgets.py]..., `PianoKeyboard` now tracks per-note velocity for active notes and uses that to tint active keys...
> In [app.py]..., playback note events now pass velocity through to both: the main keyboard, the Pianola per-track keyboards...
> I added coverage in: [test_widgets.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 162 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add velocity tinting to Piano keyboards" \
  -m "- Track per-note velocity in PianoKeyboard for active notes" \
  -m "- Tint active keys based on intensity instead of uniform color" \
  -m "- Pass velocity from playback events to main and Pianola keyboards" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new visual docs" \
  -m "- Add tests for velocity storage, clearing, and color variation" \
  -m "- Validation: compileall OK, 162 tests pass"
```

---

## 31. Piano Player: Note Labels

**Texto Original:**
> We kept the Pianola work moving and finished the note-label modes.
> In [widgets.py]..., `PianoKeyboard` now supports note-name display modes: `never`, `minimal`, `active`, `always`... I also added note-name generation (`C4`, `A#3`, etc.)...
> In [app.py]..., the `Piano Player` dialog now has a `Labels` selector...
> I added coverage in: [test_widgets.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 164 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add configurable note labels to Piano keyboards" \
  -m "- Support never/minimal/active/always display modes in PianoKeyboard" \
  -m "- Implement note-name generation (e.g., C4, A#3) for all keys" \
  -m "- Add Labels selector to PianolaDialog with status bar feedback" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new label docs" \
  -m "- Add tests for label sets, formatting, and UI wiring" \
  -m "- Validation: compileall OK, 164 tests pass"
```

---

## 32. Piano Player: Color Modes

**Texto Original:**
> We kept the Pianola window moving and finished the color-control item.
> In [widgets.py]..., `PianoKeyboard` now supports configurable active-color palettes...
> In [app.py]..., the `Piano Player` dialog now has a `Colors` selector with: `Blue`, `By channel`...
> I added coverage in: [test_widgets.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 166 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add per-channel color modes to Piano Player" \
  -m "- Support configurable active-color palettes in PianoKeyboard widget" \
  -m "- Add Colors selector with Blue and By channel options" \
  -m "- Assign color families based on primary MIDI channel for distinction" \
  -m "- Maintain velocity tinting compatibility with new palettes" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new color docs" \
  -m "- Add tests for palette overrides and channel-based coloring" \
  -m "- Validation: compileall OK, 166 tests pass"
```

---

## 33. Piano Player: Octave Designation

**Texto Original:**
> We kept the Pianola work moving and finished configurable octave designation.
> In [widgets.py]..., `PianoKeyboard` now supports an octave offset for note labels...
> In [app.py]..., the `Piano Player` dialog now has an `Octaves` selector with: `Scientific`, `Yamaha`...
> I added coverage in: [test_widgets.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 168 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): add configurable octave designation to Pianola" \
  -m "- Support octave offset in PianoKeyboard for Scientific/Yamaha modes" \
  -m "- Add Octaves selector to PianolaDialog with live label updates" \
  -m "- Report octave mode changes in main window status bar" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new notation docs" \
  -m "- Add tests for label shifting and UI wiring behavior" \
  -m "- Validation: compileall OK, 168 tests pass"
```

---

## 34. Piano Player: Manual Input

**Texto Original:**
> We pushed the Pianola work into real interaction: the keyboards can now be played.
> In [widgets.py]..., `PianoKeyboard` now supports: mouse note playing, computer-keyboard note playing, `notePressed` / `noteReleased` signals...
> In [app.py]..., I wired those signals into real outgoing MIDI: the main keyboard sends manual notes on channel 1, each Pianola track keyboard sends notes on that track’s primary MIDI channel...
> I added coverage in: [test_widgets.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 172 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(ui): enable manual note playing on Pianola keyboards" \
  -m "- Add mouse and QWERTY keyboard input support to PianoKeyboard widget" \
  -m "- Implement notePressed/noteReleased signals with hit-testing" \
  -m "- Wire main keyboard to channel 1 and track keyboards to their channels" \
  -m "- Update level meters and event labels for manual note activity" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new interaction docs" \
  -m "- Add tests for key mapping, signal emission, and MIDI routing" \
  -m "- Validation: compileall OK, 172 tests pass"
```

---

## 35. Preferences: Player Piano Tab

**Texto Original:**
> We moved a solid preferences slice forward: the `Player Piano` tab is now real and persisted.
> In [settings.py]..., I added stored Pianola preferences for: color mode, note-name display mode, octave designation...
> In [app.py]..., the `Preferences` dialog now has a `Player Piano` tab with controls for those three options...
> I updated the fake settings and tests in: [test_settings.py], [test_app_playlist.py]...
> I also updated [Roadmap.md]... And I refreshed the user guides...
> Verification is clean: ... 174 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add Player Piano preferences tab" \
  -m "- Persist color mode, note labels, and octave designation settings" \
  -m "- Add Player Piano tab to PreferencesDialog with Restore Defaults" \
  -m "- Apply settings live to open Pianola windows and new instances" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new preference docs" \
  -m "- Add tests for persistence, validation, and live application" \
  -m "- Validation: compileall OK, 174 tests pass"
```

---

## 36. Preferences: Lyrics Tab

**Texto Original:**
> We pushed the preferences work further and landed a real `Lyrics` tab.
> In [settings.py]..., I added persisted Lyrics preferences for: font family, font size, future text color, past text color...
> In [app.py]..., the `Preferences` dialog now has a `Lyrics` tab with controls for those values...
> I also updated `LyricsDialog` so its highlighted HTML uses configurable past/future colors...
> Tests were expanded in: [test_settings.py], [test_app_playlist.py]...
> I updated [Roadmap.md]... And I refreshed the user guides...
> Verification is clean: ... 176 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add Lyrics preferences tab" \
  -m "- Persist font family, size, and past/future text colors" \
  -m "- Add Lyrics tab to PreferencesDialog with Restore Defaults support" \
  -m "- Apply settings live to open Lyrics windows and new instances" \
  -m "- Update LyricsDialog HTML rendering to use configurable colors" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new preference docs" \
  -m "- Add tests for persistence, clamping, and live application" \
  -m "- Validation: compileall OK, 176 tests pass"
```

---

## 37. Preferences: Note-Name Font

**Texto Original:**
> We kept the preferences work moving and finished another real `Player Piano` item: note-name font.
> In [widgets.py]..., `PianoKeyboard` now has a configurable note-label font...
> In [settings.py]..., I added persisted Player Piano font settings for: note-name font family, note-name font size...
> In [app.py]..., the `Preferences` dialog’s `Player Piano` tab now includes: `Note-name font`, `Note-name size`...
> Tests were expanded in: [test_settings.py], [test_app_playlist.py]...
> I updated [Roadmap.md]... and refreshed the user guides...
> Verification is clean: ... 176 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add configurable note-name font to Pianola" \
  -m "- Support custom font family and size in PianoKeyboard widget" \
  -m "- Persist note-name font settings in Player Piano preferences tab" \
  -m "- Apply font changes live to open Pianola windows and new instances" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new font docs" \
  -m "- Add tests for persistence, clamping, and live application" \
  -m "- Validation: compileall OK, 176 tests pass"
```

---

## 38. Preferences: Single Highlight Color

**Texto Original:**
> We kept the port moving and finished another real `Player Piano` preferences item: single highlight color.
> In [settings.py]..., I added a persisted `pianola/single_color` setting with a default blue highlight. In [app.py]..., the `Preferences -> Player Piano` tab now includes `Single highlight color`...
> I also updated the related docs in [Roadmap.md], [EN guide], and [ES guide], and extended tests...
> Verification is clean: ... 176 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add single highlight color to Pianola prefs" \
  -m "- Persist pianola/single_color setting with default blue highlight" \
  -m "- Add Single highlight color control to Preferences Player Piano tab" \
  -m "- Apply custom color live when Highlight colors is set to Single color" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new color docs" \
  -m "- Add tests for persistence, defaults, and live application" \
  -m "- Validation: compileall OK, 176 tests pass, offscreen verified"
```

---

## 39. Preferences: Velocity Tinting Toggle

**Texto Original:**
> We kept the port moving and finished another `Preferences -> Player Piano` item: velocity tinting is now a real saved option.
> In [drumstick/drumstick_py/widgets.py]..., `PianoKeyboard` now has a `set_velocity_tinting_enabled()` switch...
> In [settings.py]..., I added persisted `pianola/velocity_tinting` with a default of `True`.
> In [app.py]..., the `Player Piano` tab now includes `Use note velocity for highlight strength`...
> Tests were expanded in [test_widgets.py], [test_settings.py], and [test_app_playlist.py]...
> Verification is clean: ... 178 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): add velocity tinting toggle to Pianola prefs" \
  -m "- Implement set_velocity_tinting_enabled() in PianoKeyboard widget" \
  -m "- Persist pianola/velocity_tinting setting with default True" \
  -m "- Add checkbox to Preferences Player Piano tab for live control" \
  -m "- Apply preference immediately to open and new Pianola windows" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new option docs" \
  -m "- Add tests for widget toggle, persistence, and live application" \
  -m "- Validation: compileall OK, 178 tests pass, offscreen verified"
```

---

## 40. Per-Song Settings Implementation

**Texto Original:**
> We pushed a bigger piece through this time: the first real per-song settings implementation is now in the PyQt6 port.
> In [app.py]..., I added: `File -> Song Settings -> Load`, `File -> Song Settings -> Save`, a new `General` preference: `Automatically load and save song settings`...
> Song settings are now stored in `$HOME/.dmidiplayer` using the loaded song filename plus `.cfg`, and they currently save/load: lyrics/text encoding, MIDI file path, transpose, tempo, global volume, per-channel volume, editable channel label, program, solo, mute, lock...
> In [settings.py]..., the new persisted preference is `general/auto_song_settings`...
> Tests were expanded in: [test_settings.py], [test_app_playlist.py]...
> Verification is clean: ... 180 tests OK...

**Comando Generado:**
```bash
git commit -m "feat(app): implement per-song settings persistence" \
  -m "- Add File > Song Settings Load/Save actions and auto-load pref" \
  -m "- Persist channel state (vol, label, program, mute/solo/lock) per song" \
  -m "- Save lyrics encoding, transpose, tempo, and volume in .cfg files" \
  -m "- Unify channel label state across Channels window instances" \
  -m "- Update user guides (EN/ES) and Roadmap.md with new feature docs" \
  -m "- Add tests for cfg I/O, auto-loading, and preference persistence" \
  -m "- Validation: compileall OK, 180 tests pass, offscreen verified"
```

---

## 41. WPS Dicts: Initial Generation

**Texto Original:**
> Hecho. Generé los diccionarios en: [build/wps-libreoffice-dicts]...
> Resultado: 51 carpetas de idioma... De esas, 47 usan los `.aff/.dic` actualizados de LibreOffice y 4 quedaron con respaldo del WPS antiguo...
> También dejé un reporte con el origen exacto de cada idioma aquí: [BUILD_SOURCE_MAP.txt]...
> Verificación realizada: no falta ningún `dict.conf`, `main.aff` ni `main.dic` en las 51 carpetas.

*(Nota: Este fue un paso intermedio antes de añadir las variantes regionales).*

---

## 42. WPS Dicts: Regional Variants

**Texto Original:**
> Hecho. Creé 20 carpetas nuevas en: [build/wps-libreoffice-dicts]...
> Nuevas variantes agregadas: de_AT, de_CH, en_CA, en_ZA, es_CR, es_CU, es_DO, es_EC, es_GQ, es_GT, es_HN, es_NI, es_PA, es_PE, es_PH, es_PY, es_SV, es_US, es_UY, es_VE...
> También actualicé el reporte: [BUILD_SOURCE_MAP.txt]...
> Verificación: ahora hay 71 carpetas en total y 213 archivos esperados...

**Comando Generado:**
```bash
git commit -m "feat(dict): expand WPS dictionaries with LibreOffice variants" \
  -m "- Generate 71 language folders with dict.conf, main.aff, and main.dic" \
  -m "- Add 20 new regional variants (de_AT, en_CA, es_*, etc.)" \
  -m "- Fallback to legacy WPS dicts for km_KH, ms_MY, qu_EC, sw_TZ" \
  -m "- Exclude generic 'es' due to missing base orthographic files" \
  -m "- Update BUILD_SOURCE_MAP.txt with exact origin for each language" \
  -m "- Verify integrity: 71 folders x 3 files = 213 files present"
```

---

## 43. WPS Dicts: Converter Tool

**Texto Original:**
> Hecho. Creé el programa PyQt6 en: [tools/wps_libreoffice_dict_converter.py]...
> Qué hace: Muestra a la izquierda los diccionarios fuente de LibreOffice. Muestra a la derecha los destinos WPS... Verifica antes de convertir... Sólo habilita `Convert` si no hay errores bloqueantes. Regenera `BUILD_SOURCE_MAP.txt` al convertir.
> Verifiqué dos cosas: python3 -m py_compile... y el analizador interno detecta: 71 mappings, 0 blocking errors, 5 warnings...

**Comando Generado:**
```bash
git commit -m "feat(tools): add PyQt6 dictionary converter GUI" \
  -m "- Implement side-by-side view for LibreOffice sources and WPS targets" \
  -m "- Validate .aff/.dic pairs, dict.conf, and special case mappings" \
  -m "- Handle legacy fallbacks for km_KH, ms_MY, qu_EC, sw_TZ" \
  -m "- Enable Convert only when no blocking errors are detected" \
  -m "- Auto-regenerate BUILD_SOURCE_MAP.txt upon successful conversion" \
  -m "- Verify compilation and internal logic (71 mappings, 0 errors)"
```

---

## 44. WPS Dicts: Repo Setup & README

**Texto Original:**
> Listo. Hice dos cambios:
> Creé [.gitignore]... ignorando cachés de Python... pero manteniendo versionable `build/wps-libreoffice-dicts`.
> Actualicé [README.md]... eliminé `# Tutorial en construcción...`, corregí la instalación para usar: `sudo cp -r build/wps-libreoffice-dicts/* /opt/kingsoft/wps-office/office6/dicts/spellcheck/`... y añadí al final la explicación de la herramienta PyQt6...

**Comando Generado:**
```bash
git commit -m "docs(repo): add .gitignore and update README with install steps" \
  -m "- Create .gitignore to exclude caches, venvs, and temp files" \
  -m "- Explicitly keep build/wps-libreoffice-dicts versioned" \
  -m "- Remove 'under construction' notice from README.md" \
  -m "- Add sudo cp installation command for WPS spellcheck dicts" \
  -m "- Document PyQt6 converter tool usage and validation logic" \
  -m "- Clarify side-by-side comparison and error-blocking behavior"
```

---

## 45. WPS Dicts: Enriched Configs (Batch 1)

**Texto Original:**
> Listo. Enriquecí los 20 `dict.conf` nuevos de `build/wps-libreoffice-dicts` para que tengan el mismo estilo de los originales de WPS: [Dictionary] DisplayName=... DisplayName[zh_CN]=... etc.
> También actualicé [tools/wps_libreoffice_dict_converter.py] para que, en futuras conversiones, genere esos `dict.conf` enriquecidos automáticamente.
> Verifiqué: 20 dict.conf nuevos actualizados, 8 DisplayName por archivo...

**Comando Generado:**
```bash
git commit -m "feat(dict): enrich dict.conf with localized display names" \
  -m "- Add DisplayName entries for zh_CN, en_US, es_ES, and other locales" \
  -m "- Update converter tool to auto-generate enriched configs" \
  -m "- Apply changes to 20 new regional variant folders" \
  -m "- Verify compilation and mapping integrity (71 mappings, 0 errors)"
```

---

## 46. WPS Dicts: Enriched Configs (Batch 2)

**Texto Original:**
> Hecho. Enriquecí estos tres archivos: hr_HR/dict.conf, km_KH/dict.conf, qu_EC/dict.conf...
> Ahora cada uno tiene 8 entradas `DisplayName`... También dejé `km_KH` con nombre local en jemer: `ភាសាខ្មែរ (កម្ពុជា)`.

**Comando Generado:**
```bash
git commit -m "feat(dict): enrich hr_HR, km_KH, and qu_EC dict configs" \
  -m "- Add 8 localized DisplayName entries to match WPS standards" \
  -m "- Include native Khmer script for km_KH display name" \
  -m "- Ensure consistency across all regional variant configurations"
```

---

## 47. WPS Dicts: README Tables

**Texto Original:**
> Listo. Añadí en [README.md]... una sección **Diccionarios disponibles** con una tabla de los 71 diccionarios...
> Debajo agregué otra tabla titulada **Diccionarios añadidos desde otras fuentes**, destacando: hr_HR, km_KH, qu_EC...
> También añadí una nota explicando que esos tres usan el mismo formato final de WPS... y que sus `dict.conf` incluyen nombres localizados...

**Comando Generado:**
```bash
git commit -m "docs(readme): add available dictionaries tables" \
  -m "- List all 71 dictionaries in build/wps-libreoffice-dicts" \
  -m "- Highlight hr_HR, km_KH, and qu_EC as added from other sources" \
  -m "- Note localized dict.conf support for improved UI display" \
  -m "- Clarify consistent WPS format (conf/aff/dic) across all entries"
```

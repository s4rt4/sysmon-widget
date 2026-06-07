"""Window manager hints for the GNOME (mutter) target.

This is the ``fedora-gnome`` branch. The widget runs as an X11 client through
XWayland, so the hints below are interpreted by mutter's XWayland bridge, not by
a classic EWMH window manager like KWin. What mutter actually honors for an
external XWayland client:

* ``_MOTIF_WM_HINTS`` undecorated  -> honored (no titlebar/border).
* ``_NET_WM_STATE_STICKY``         -> honored (shown on every workspace).
* ``_NET_WM_STATE_SKIP_TASKBAR``   -> honored (hidden from dash/alt-tab list).
* ``_NET_WM_STATE_SKIP_PAGER``     -> honored.
* ``_NET_WM_STATE_BELOW``          -> honored *relative to other windows*; it
  stays beneath normal app windows but mutter will NOT push it beneath the
  wallpaper/desktop the way KWin does. True conky-style "glued to the desktop"
  is not achievable for an external client on mutter -- this is the closest.

Deliberately NOT used on GNOME:

* ``_NET_WM_WINDOW_TYPE_DESKTOP`` -> mutter manages desktop-type surfaces as a
  shell component; an external XWayland client set to this type loses input
  routing and stacking behaves erratically. We keep the NORMAL type instead.
"""

_WARNED = False

# States mutter honors for an XWayland client. BELOW is appended on request.
_BASE_STATES = ("_NET_WM_STATE_STICKY", "_NET_WM_STATE_SKIP_TASKBAR", "_NET_WM_STATE_SKIP_PAGER")


def apply_desktop_hints(wid: int, desktop_type: bool = False, splash_type: bool = False, below: bool = True, undecorated: bool = True):
    """Apply window hints, swallowing failures so the widget still starts.

    ``desktop_type``/``splash_type`` are accepted for API parity with the
    ``kde-x11`` branch but ignored on GNOME (see module docstring); the window
    is always kept as NORMAL type here.
    """
    global _WARNED
    try:
        set_window_hints(wid, below=below, undecorated=undecorated)
    except Exception as exc:
        if not _WARNED:
            print(f"Xlib hints unavailable (running outside X11/XWayland?): {exc}")
            _WARNED = True


def set_window_hints(wid: int, below: bool = True, undecorated: bool = True):
    from Xlib import X, display
    from Xlib.protocol import event
    from Xlib.Xatom import ATOM, CARDINAL

    d = display.Display()
    root = d.screen().root
    win = d.create_resource_object("window", wid)

    def atom(name: str):
        return d.intern_atom(name)

    # Keep NORMAL type on GNOME -- DESKTOP/SPLASH break input/stacking on mutter.
    win.change_property(
        atom("_NET_WM_WINDOW_TYPE"),
        ATOM,
        32,
        [atom("_NET_WM_WINDOW_TYPE_NORMAL")],
    )

    if undecorated:
        # _MOTIF_WM_HINTS: flags=2 (decorations), decorations=0 (none)
        mwm_atom = atom("_MOTIF_WM_HINTS")
        win.change_property(mwm_atom, mwm_atom, 32, [2, 0, 0, 0, 0])

    states = list(_BASE_STATES)
    if below:
        states.append("_NET_WM_STATE_BELOW")

    # Set as a property (applies before map) AND send client messages (applies
    # after the window is already mapped/managed). mutter needs the latter for
    # state changes on a live window.
    win.change_property(
        atom("_NET_WM_STATE"),
        ATOM,
        32,
        [atom(s) for s in states],
    )
    # Sticky implies "all desktops".
    win.change_property(atom("_NET_WM_DESKTOP"), CARDINAL, 32, [0xFFFFFFFF])

    for state in states:
        message = event.ClientMessage(
            window=win,
            client_type=atom("_NET_WM_STATE"),
            data=(32, [1, atom(state), 0, 1, 0]),  # _NET_WM_STATE_ADD, source=app
        )
        root.send_event(message, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)

    d.sync()
    d.close()


def query_state(wid: int):
    """Return the list of ``_NET_WM_STATE_*`` atom names mutter currently keeps
    on the window. Used to verify empirically which hints survived; safe to call
    in production (returns ``[]`` on any failure)."""
    try:
        from Xlib import display
        from Xlib.Xatom import ATOM

        d = display.Display()
        try:
            win = d.create_resource_object("window", wid)
            prop = win.get_full_property(d.intern_atom("_NET_WM_STATE"), ATOM)
            if prop is None:
                return []
            return [d.get_atom_name(a) for a in prop.value]
        finally:
            d.close()
    except Exception:
        return []

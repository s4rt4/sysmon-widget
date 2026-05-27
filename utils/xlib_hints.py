_WARNED = False


def apply_desktop_hints(wid: int, desktop_type: bool = False, splash_type: bool = False, below: bool = True, undecorated: bool = True):
    global _WARNED
    try:
        set_window_hints(wid, desktop_type=desktop_type, splash_type=splash_type, below=below, undecorated=undecorated)
    except Exception as exc:
        if not _WARNED:
            print(f"Xlib hints unavailable: {exc}")
            _WARNED = True


def set_window_hints(wid: int, desktop_type: bool = False, splash_type: bool = False, below: bool = True, undecorated: bool = True):
    from Xlib import X, display
    from Xlib.protocol import event
    from Xlib.Xatom import ATOM, CARDINAL

    d = display.Display()
    root = d.screen().root
    win = d.create_resource_object("window", wid)

    def atom(name: str):
        return d.intern_atom(name)

    if desktop_type:
        window_type = "_NET_WM_WINDOW_TYPE_DESKTOP"
    elif splash_type:
        window_type = "_NET_WM_WINDOW_TYPE_SPLASH"
    else:
        window_type = "_NET_WM_WINDOW_TYPE_NORMAL"
    win.change_property(
        atom("_NET_WM_WINDOW_TYPE"),
        ATOM,
        32,
        [atom(window_type)],
    )

    if undecorated:
        # _MOTIF_WM_HINTS: flags=2 (decorations), decorations=0 (none)
        mwm_atom = atom("_MOTIF_WM_HINTS")
        win.change_property(mwm_atom, mwm_atom, 32, [2, 0, 0, 0, 0])

    states = ["_NET_WM_STATE_STICKY", "_NET_WM_STATE_SKIP_TASKBAR", "_NET_WM_STATE_SKIP_PAGER"]
    if below:
        states.append("_NET_WM_STATE_BELOW")
    win.change_property(
        atom("_NET_WM_STATE"),
        ATOM,
        32,
        [atom(s) for s in states],
    )
    win.change_property(atom("_NET_WM_DESKTOP"), CARDINAL, 32, [0xFFFFFFFF])

    for state in states:
        message = event.ClientMessage(
            window=win,
            client_type=atom("_NET_WM_STATE"),
            data=(32, [1, atom(state), 0, 1, 0]),
        )
        root.send_event(message, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)

    d.sync()
    d.close()

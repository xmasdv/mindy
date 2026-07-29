/**
 * HTML body element handling the general layout of the about3pane.
 */
var paneLayout;

/**
 * HTML element handling the swap between message, multimessage, and browser
 * XUL views.
 */
var messagePane;

  updateZoomCommands();

  // Update the state of the about:3pane being fully loaded.
  hasDOMContentLoaded.resolve();
});

window.addEventListener("unload", () => {
  folderPane.uninit();
  threadPane.uninit();
  threadPaneHeader.uninit();
});

import {Config} from '@remotion/cli/config';
// Chromium del contenedor (el "headless shell" es el único que Remotion acepta aquí)
Config.setBrowserExecutable('/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell');
Config.setConcurrency(4);

import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer("angle"); // WebGL por software (sin GPU) para las escenas 3D
Config.setBrowserExecutable(process.env.CHROMIUM_PATH ?? null);
Config.setConcurrency(2);

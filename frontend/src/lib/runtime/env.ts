// SPDX-FileCopyrightText: 2026 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

/**
 * This wrapper allow to both, frontend and backend, to get env vars that are set at runtime in the Dockerfile.
 * It will first try to get the env var from the window object, if it fails (which means we are in the backend), it will try to get it from process.env.
 */
export const runtimeEnvVarWrapper = {

    /**
     * This function allow to get env vars that are set at runtime in the Dockerfile
     * @param name Name of the env var we want
     * @returns Value of the env var
     */
    get(name: string): string | undefined {
        try {
            return window.env[name];
        }
        catch (_) {
            return process.env[name];
        }
    }
};

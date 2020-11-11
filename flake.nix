## Use "use flake" in .envrc
## $ echo "use flake" > .envrc
{
  description = "Website of Léo Colisson";
  ###### Inputs
  inputs.nixpkgs.url = github:NixOS/nixpkgs/nixos-unstable;
  inputs.flake-utils.url = "github:numtide/flake-utils";
  # uikit is used as a CSS framework (similar to bootstrap)
  inputs.uikit-src = {
    url = "github:uikit/uikit/v3.5.9";
    flake = false;
  };
  ###### Outputs
  outputs = { self, nixpkgs, flake-utils, uikit-src }:
    # See https://github.com/numtide/flake-utils
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          haskellPackages' = pkgs.callPackage ./hpkgs.nix { };
          colissonWebsite = pkgs.callPackage ./website.nix {
            # We need to add some libraries, including uikit (bootstrap-like css framework)
            # linkFarm creates a folder with a subfolder uikit pointing to the sources of uikit.
            sassLoadPath = [{
              name = "uikit";
              path = "${uikit-src}";
            }];
            haskellPackages = haskellPackages';
          };
        in
        rec {
          # Packages that are created by this lib
          # It is what "nix build .#name" will compile
          # For example "nix build .#mysatsolver"
          packages = flake-utils.lib.flattenTree { inherit colissonWebsite; };
          # What package "nix build ." will compile by default:
          defaultPackage = colissonWebsite.colissonExecutableWithThirdParties;
          # The apps can be run directly via "nix run .#name-of-the-app"
          # Example: "nix run .#mysatsolver"
          apps.colissonExecutable = flake-utils.lib.mkApp {
            drv = packages.colissonExecutable;
            # Customize the path of the binary to run
            exePath = "/bin/site";
          };
          # What "nix run ." will run by default (you can give arguments like
          # "nix run . -- my args goes here")
          defaultApp = apps.colissonExecutable;
          # Run the shell with "nix develop"
          devShell = colissonWebsite.shell;
        });
}

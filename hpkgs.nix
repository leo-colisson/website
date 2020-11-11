# hpkgs.nix

{ compiler ? "ghc884"
, lib
, pkgs
, fetchFromGitHub
}:

let
  inherit (pkgs.lib.trivial) flip pipe;
  inherit (pkgs.haskell.lib) appendPatch appendConfigureFlags;
    
  hakyllFlags = [ "-f" "watchServer" "-f" "previewServer" ];

  haskellPackages = pkgs.haskell.packages.${compiler}.override {
    overrides = hpNew: hpOld: {
      hakyll =
        # pipe is used to apply all the following rules
        # sequentially in order to override the initial hpOld.hakyll derivation
        pipe
          hpOld.hakyll
          (with pkgs.haskell.lib; [
            # See the file pkgs/development/haskell-modules/lib.nix for a list of such functions:
            # Apply a patch (can be created with "git diff > ../hakyll.patch")
            (flip appendPatch ./hakyll.patch)
            # We force the above flags, since cabal may silently disable them if a dependency is missing
            (flip appendConfigureFlags hakyllFlags)
            unmarkBroken
            # doJailbreak # Useless since it is inside a condition
            # To do tests:
            # (flip overrideSrc {src = ./hakyll; })
            (flip overrideSrc {src = fetchFromGitHub {
                                 owner = "jaspervdj";
                                 repo = "hakyll";
                                 rev = "e9a8139152b166eae75083259fc3e824675de6fb";
                                 sha256 = "rWd5tSGyPB/vvlhOuDKC85onx2d5+lApTS1lqRJrwpg=";
                               };})
          ]);

      # ...
    };
  };
in haskellPackages



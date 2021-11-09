{ # sassLoadPath will be given to sass, in order to let him find all the
  # libraries (for example uikit). linkFarm is a practical trivial nix builder
  # that can be used to create such folder.
  sassLoadPath ? [],
  lib,
  makeWrapper,
  mkShell,
  linkFarm,
  sass,
  entr,
  haskellPackages,
  hlint,
  cabal-install,
  ghcid,
  writeShellScriptBin,
  runCommand,
  stdenv,
}:
let
  # This is the compiled site.hs. However, in order to include CSS libraries
  # (uikit), you may prefer the colissonExecutableWithThirdParties output
  colissonExecutable = haskellPackages.callCabal2nix "colisson" ./src {};
  sassLoadPath' = linkFarm "sassLoadPath" sassLoadPath;
  # It appears that in order to compile the .scss files, we need some libraries
  # (uikit in our case), so we give the path of the library to our executable
  # using an environment variable.
  # Inspired by https://github.com/ysndr/blog
  colissonExecutableWithThirdParties =
    colissonExecutable.overrideAttrs (
      old: {
        nativeBuildInputs = (old.nativeBuildInputs or []) ++ [ makeWrapper ];
        installPhase = old.installPhase + "\n" + ''
            wrapProgram $out/bin/site --set-default SASSLOADPATH ${sassLoadPath'} --prefix PATH : ${lib.makeBinPath [
              sass
            ]}
          '';
      }
    );
  compileAndWatch = writeShellScriptBin "compile_and_watch" ''
    echo site.hs | entr -n -r -s 'ghc --make site.hs && (echo site | entr -n -r -s "./site clean && ./site watch")'
  '';
  deployCurrentVersion = writeShellScriptBin "deploy_current_version" ''
    rsync -az --delete _site/ colisson.me:/website/
  '';
  # This is the final static, compiled, website
  # colissonStaticWebsite = runCommand "colissonStaticWebsite" ''
  #   cd src && ${colissonExecutableWithThirdParties}/bin/site build && mkdir -p $out && cp -r _site $out
  # '';
  colissonStaticWebsite = stdenv.mkDerivation {
    name = "colissonStaticWebsite";
    src = ./src;
    nativeBuildInputs = [ colissonExecutableWithThirdParties ];
    installPhase = ''
      mkdir -p $out
      echo "Cleaning..."
      ${colissonExecutableWithThirdParties}/bin/site clean
      echo "Building..."
      ls -al
      ls templates
      ${colissonExecutableWithThirdParties}/bin/site build
      cp -r _site $out
    '';
  };

  # This shell provides some useful commands to develop:
  shell = mkShell {
    name = "website-dev";
    buildInputs = [
      (haskellPackages.ghcWithPackages (p: [p.hakyll p.ghcid]))
      sass
      entr
      hlint
      cabal-install
      ghcid
      compileAndWatch
      deployCurrentVersion
    ];
    shellHook = ''
      export SASSLOADPATH="${sassLoadPath'}"
      echo "You can now go to your favorite folder and type 'compile_and_watch' to recompile your website"
      echo "at every change."
    '';
  };
in
{
  inherit colissonExecutable colissonExecutableWithThirdParties colissonStaticWebsite shell;
}

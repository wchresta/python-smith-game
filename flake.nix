{
  outputs = { self, nixpkgs, flake-utils, mach-nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        mach-nix-lib = import mach-nix {
          inherit pkgs;
          python = "python310";
        };

        python-smith-game = mach-nix-lib.mkPython {
          requirements = builtins.readFile ./requirements.txt;
        };
      in {
        packages = { inherit python-smith-game; };
        defaultPackage = python-smith-game;

        devShell = pkgs.mkShell {
          inputsFrom = builtins.attrValues self.packages.${system};
          buildInputs = with pkgs; [
            black
            mypy
          ];
        };
      });
}

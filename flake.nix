{

  inputs.cq-flake.url = github:thelegy/cq-flake;
  inputs.cq-wild = {
    url = github:thelegy/cq-wild;
    inputs.cq-flake.follows = "cq-flake";
    inputs.nixpkgs.follows = "cq-flake/nixpkgs";
  };
  inputs.nixpkgs = {
    url = github:NixOS/nixpkgs;
    follows = "cq-flake/nixpkgs";
  };

  outputs = { nixpkgs, cq-flake, cq-wild, self }: {

    overlays.default = final: prev: {
      pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
        (pfinal: pprev: {
          cq-gridbase = pfinal.callPackage ./default.nix {};
        })
      ];
    };

    packages.x86_64-linux = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [
          cq-flake.overlays.default
          cq-wild.overlays.default
          self.overlays.default
        ];
      };
    in {
      default = pkgs.pythonCQ.withPackages (p: [p.cq-gridbase]);
    };

    devShells.x86_64-linux = let
      pkgs = import nixpkgs {
        system = "x86_64-linux";
        overlays = [
          cq-flake.overlays.default
          cq-wild.overlays.default
          self.overlays.default
        ];
      };
    in {
      default = pkgs.mkShell {
        inputsFrom = [ pkgs.pythonCQPackages.cq-gridbase ];
        nativeBuildInputs = [ pkgs.cq-editor ];
      };
    };

  };

}

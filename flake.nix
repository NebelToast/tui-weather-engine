{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.ncurses
          pkgs.ruff

          (pkgs.python311.withPackages (python-pkgs: with python-pkgs; [
            toml
            
          ]))
        ];

      };
    };
}
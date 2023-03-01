{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  outputs = { self, nixpkgs } : rec
  {
    system = "x86_64-linux";
    packages.x86_64-linux.default = 
      with import nixpkgs {inherit system;};
      python3Packages.buildPythonPackage {
        pname = "flohmarkt";
        name = "flohmarkt";
        src = ./.;
        nativeBuildInputs = [
          python3
          python3Packages.fastapi
          python3Packages.uvicorn
        ];
        propagatedBuildInputs = [
          python3
          python3Packages.fastapi
          python3Packages.uvicorn
        ];
      };
    devShell.x86_64-linux =
      with import nixpkgs {inherit system;};
      mkShell {
        name = "flohmarkt devshell";
        buildInputs = [
          python3
          python3Packages.fastapi
          python3Packages.uvicorn
        ];
    };
    nixosModule.default = { config, lib, ... }:
      {
        options = {

          services.devflake = {

            enable = lib.mkOption {
              default = false;
              type = lib.types.bool;
              description = ''
                Enable agent service. Use this to disable but still install the service at packer time.
              '';
            };

          };
        };

        config = lib.mkIf config.services.devflake.enable {
          systemd.services.devflake = {
            description = "flek runner";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            script = ''
              cd ${./.}
              ${nixpkgs.legacyPackages.x86_64-linux.python3Packages.uvicorn}/bin/uvicorn devflake:app
            '';
          };

          environment.systemPackages = [ packages.x86_64-linux.default ] ++ [
                nixpkgs.legacyPackages.x86_64-linux.python3
                nixpkgs.legacyPackages.x86_64-linux.python3Packages.fastapi
                nixpkgs.legacyPackages.x86_64-linux.python3Packages.uvicorn
          ];
        };
      };
  };
}

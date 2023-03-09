{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  outputs = { self, nixpkgs } : 
  let 
    depfun = p: [
      p.uvicorn
      p.fastapi
      p.motor
    ];
  in
  rec
  {
    system = "x86_64-linux";
    packages.x86_64-linux.default = 
      with import nixpkgs {inherit system;};
      python3Packages.buildPythonPackage {
        pname = "flohmarkt";
        name = "flohmarkt";
        src = ./.;
        propagatedBuildInputs = [
          python3
        ] ++ depfun python3Packages;
      };
    devShell.x86_64-linux =
      with import nixpkgs {inherit system;};
      mkShell {
        name = "flohmarkt devshell";
        buildInputs = [
          python3
        ] ++ depfun python3Packages;
    };
    nixosModule.default = { config, lib, ... }:
      {
        options = {
          services.flohmarkt = {
            enable = lib.mkOption {
              default = false;
              type = lib.types.bool;
              description = ''
                Enable flohmarkt service.
              '';
            };
          };
        };

        config = lib.mkIf config.services.flohmarkt.enable {
          systemd.services.flohmarkt = {
            description = "Flohmarkt Webservice";
            wantedBy = [ "multi-user.target" ];
            after = [ "network.target" ];
            script = ''
              cd ${./.}
              ${nixpkgs.legacyPackages.x86_64-linux.python3.withPackages (p: depfun p ++ [packages.x86_64-linux.default ])}/bin/uvicorn flohmarkt:app --host 0.0.0.0 --port 8080
            '';
          };
        };
      };
  };
}

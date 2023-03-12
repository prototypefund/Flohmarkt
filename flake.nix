{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  outputs = { self, nixpkgs } : 
  let 
    depfun = p: [
      p.uvicorn
      p.fastapi
      p.motor
      p.pyjwt
      p.email-validator
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

        environment.etc."flohmarkt.conf" = {
          text = ''
            [General]
            InstanceName = Fluffys Flohmarkt
            ExternalURL = http://fluffy.cat
            DebugMode = 0
            JwtSecret = S0op3rs3cr3t

            [Database]
            Server = 192.168.0.52
            Port = 27017
            User = foo
            Password = bar

            [SMTP]
            Server = mail.foo.org
            Port = 587
            User = user@foobar.org
            Password = S0op3rs3cr3t
          '';
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

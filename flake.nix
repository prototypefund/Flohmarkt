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

        doCheck = false;
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
            settings = {
              general = {
                instanceName = lib.mkOption {
                  default = "Fluffys Flomarkt";
                  type = lib.types.str;
                  description = ''
                    The name the Instance will be presented with
                    to the users
                  '';
                };
                externalUrl = lib.mkOption {
                  default = "https://example.org";
                  type = lib.types.str;
                  description = ''
                    The external URL under which this instance will
                    be available
                  '';
                };
                debugMode = lib.mkOption {
                  default = 0;
                  type = lib.types.int;
                  description = ''
                    If this is 1, debug mode will be active.
                    WARNING: Running in Debug may compromise
                    your operational security.
                  '';
                };
                jwtSecret = lib.mkOption {
                  default = "S0op3rs3cr3t";
                  type = lib.types.str;
                  description = ''
                    This is the secret that will be used for HS256
                    JWT generation and validation.
                  '';
                };
              };
              database = {
                server = lib.mkOption {
                  default = "127.0.0.1";
                  type = lib.types.str;
                  description = ''
                    The IP of the MongoDB Server we are going to connect
                    to for persistent storage
                  '';
                };
                port = lib.mkOption {
                  default = 27017;
                  type = lib.types.int;
                  description = ''
                    The Port MongoDB Server we are going to connect
                    to for persistent storage
                  '';
                };
                user = lib.mkOption {
                  default = "user";
                  type = lib.types.str;
                  description = ''
                    The Username used to authenticate with MongoDB
                  '';
                };
                password = lib.mkOption {
                  default = "S0op3rs3cr3t";
                  type = lib.types.str;
                  description = ''
                    The password used to authenticate with MongoDB
                  '';
                };
              };
              smtp = {
                server = lib.mkOption {
                  default = "S0op3rs3cr3t";
                  type = lib.types.str;
                  description = ''
                    The SMTP Server used for outgoing mail
                  '';
                };
                port = lib.mkOption {
                  default = 25;
                  type = lib.types.int;
                  description = ''
                    The Port we're goint to use on the SMTP Server
                  '';
                };
                user = lib.mkOption {
                  default = "user@example.org";
                  type = lib.types.str;
                  description = ''
                    The username with which we connect to the SMTP Server
                    (usually looks like an email address)
                  '';
                };
                from = lib.mkOption {
                  default = "otheruser@example.org";
                  type = lib.types.str;
                  description = ''
                    The email adress which is displayed as From-address
                    in outgoing email.
                  '';
                };
                password = lib.mkOption {
                  default = "S0op3rs3cr3t";
                  type = lib.types.str;
                  description = ''
                    The password used to authenticate with the Mailserver
                  '';
                };
                cafile = lib.mkOption {
                  default = "/some/path";
                  type = lib.types.str;
                  description = ''
                    If the SMTP-Server has a self-signed cert, place it
                    somewhere and put the path here.
                  '';
                };
              };
            };
          };
        };


        config = lib.mkIf config.services.flohmarkt.enable {
          environment.etc."flohmarkt.conf" = {
            text = ''
              [General]
              InstanceName = ${config.services.flohmarkt.settings.general.instanceName}
              ExternalURL = ${config.services.flohmarkt.settings.general.externalUrl}
              DebugMode = ${config.services.flohmarkt.settings.general.debugMode}
              JwtSecret =  ${config.services.flohmarkt.settings.general.jwtSecret}

              [Database]
              Server = ${config.services.flohmarkt.settings.database.server}
              Port = ${config.services.flohmarkt.settings.database.port}
              User = ${config.services.flohmarkt.settings.database.user}
              Password = ${config.services.flohmarkt.settings.database.password}

              [SMTP]
              Server = ${config.services.flohmarkt.settings.smtp.server}
              Port = ${config.services.flohmarkt.settings.smtp.port}
              User = ${config.services.flohmarkt.settings.smtp.user}
              From = ${config.services.flohmarkt.settings.smtp.from}
              Password = ${config.services.flohmarkt.settings.smtp.password}
              CAFile = ${config.services.flohmarkt.settings.smtp.cafile}
            '';
          };
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

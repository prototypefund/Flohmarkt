{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
  outputs = { self, nixpkgs } : 
  let 
    depfun = p: [
      p.uvicorn
      p.fastapi
      p.aiohttp
      p.pyjwt
      p.pycryptodome
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
            initialization = {
              db_admin_pw = lib.mkOption {
                default = "secretpassw0rd";
                type = lib.types.str;
                description = ''
                  The password of the database admin user
                '';
              };
              db_user_pw = lib.mkOption {
                default = "secretpassw0rd";
                type = lib.types.str;
                description = ''
                  The password of the database flohmarkt user
                '';
              };
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
                imagePath = lib.mkOption {
                  default = "/var/lib/flohmarkt";
                  type = lib.types.str;
                  description = ''
                    The path where uploaded images land.
                  '';
                };
              };
              database = {
                server = lib.mkOption {
                  default = "http://user:user@127.0.0.1:1025";
                  type = lib.types.str;
                  description = ''
                    The IP of the MongoDB Server we are going to connect
                    to for persistent storage
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
                    in outgoing email. (If mailserver allows this).
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
          users.users.flohmarkt = {
            isNormalUser = true;
            home = config.services.flohmarkt.settings.general.imagePath;
            description = "Flohmarkt Webserver User";
          };
          environment.etc."flohmarkt.conf" = {
            text = ''
              [General]
              InstanceName = ${config.services.flohmarkt.settings.general.instanceName}
              ExternalURL = ${config.services.flohmarkt.settings.general.externalUrl}
              DebugMode = ${toString config.services.flohmarkt.settings.general.debugMode}
              JwtSecret =  ${config.services.flohmarkt.settings.general.jwtSecret}
              ImagePath =  ${config.services.flohmarkt.settings.general.imagePath}

              [Database]
              Server = ${config.services.flohmarkt.settings.database.server}

              [SMTP]
              Server = ${config.services.flohmarkt.settings.smtp.server}
              Port = ${toString config.services.flohmarkt.settings.smtp.port}
              User = ${config.services.flohmarkt.settings.smtp.user}
              From = ${config.services.flohmarkt.settings.smtp.from}
              Password = ${config.services.flohmarkt.settings.smtp.password}
              CAFile = ${config.services.flohmarkt.settings.smtp.cafile}
            '';
          };

          services.couchdb = {
            enable = true;
            bindAddress = "127.0.0.1";
            port = 1025;
            adminUser = "admin";
            adminPass = config.services.flohmarkt.initialization.db_admin_pw;
          };

          systemd.services.prime_couchdb_flohmarkt = {
            description = "Flohmarkt CouchDB Primer - Fills flohmarkt DBs with indices and views";
            wantedBy = [ "flohmarkt.service" ];
            after = [ "couchdb.service" ]; # TODO: this might be a problem if couchdb is on remote host
            serviceConfig = {
              Type = "oneshot";
            };
            script = ''
              sleep 3
              echo "Initializing Database"
              cd ${./.}
              ${nixpkgs.legacyPackages.x86_64-linux.python3.withPackages (p: depfun p ++ [packages.x86_64-linux.default ])}/bin/python3 initialize_couchdb.py ${config.services.flohmarkt.initialization.db_admin_pw} ${config.services.flohmarkt.initialization.db_user_pw}
              echo "Initialized Database"
            '';
          };

          systemd.services.flohmarkt-background = {
            description = "Flohmarkt Background Tasks";
            serviceConfig = {
              User = "flohmarkt";
            };
            after = [ "network.target" ];
            script = ''
              cd ${./.}
              ${nixpkgs.legacyPackages.x86_64-linux.python3.withPackages (p: depfun p ++ [packages.x86_64-linux.default ])}/bin/python3 background.py
            '';
          };

          systemd.services.flohmarkt = {
            description = "Flohmarkt Webservice";
            serviceConfig = {
              User = "flohmarkt";
            };
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

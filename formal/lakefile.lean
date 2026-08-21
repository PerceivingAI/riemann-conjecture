import Lake
open Lake DSL

package "cert" where
  version := v!"0.1.0"

@[default_target]
lean_lib «Cert» where
  roots := #[`Cert]

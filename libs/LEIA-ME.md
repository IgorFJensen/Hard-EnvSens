# Bibliotecas do projeto Hard-EnvSens

```
libs/
  EnvSens.kicad_sym     <- TODOS os simbolos proprios (uma lib so)
  EnvSens.pretty/       <- TODOS os footprints proprios (um .kicad_mod por footprint)
  EnvSens.3dshapes/     <- modelos 3D (.step)
  Images.pretty/        <- logos da silk
```

As tabelas do projeto (sym-lib-table / fp-lib-table) ja apontam para cá.
**Nunca mais e preciso mexer em "Gerenciar bibliotecas".**

## Adicionar um componente novo (ex.: baixado do SnapEDA / Ultra Librarian / Mouser)

1. Descompacte o zip numa pasta temporaria (fora do projeto).
2. **Footprint**: copie o `.kicad_mod` para `libs/EnvSens.pretty/`.
3. **3D**: copie o `.step` para `libs/EnvSens.3dshapes/`.
   No Editor de Footprint, abra o footprint > Propriedades > Modelos 3D > `+` e use
   `${KIPRJMOD}/libs/EnvSens.3dshapes/NOME.step`. Salve.
4. **Simbolo**: Editor de Simbolos > clique na lib **EnvSens** > Arquivo > Importar Simbolo...
   escolha o `.kicad_sym` do zip. No campo *Footprint* do simbolo coloque
   `EnvSens:NOME_DO_FOOTPRINT`. Salve (Ctrl+S).
5. Pronto: o simbolo aparece em "Adicionar simbolo" dentro de **EnvSens**.

Dica: se o componente ja existe nas libs padrao do KiCad (resistor, SOT-23, etc.), use a padrao.

O backup do formato antigo (uma lib por peca) esta em `../_backup_libs_antigas/`.

{ buildPythonPackage
, cadquery
, cq-apply-to-each-face
, cq-wild
}:

buildPythonPackage {

  name = "cq-gridbase";

  src = ./.;
  format = "pyproject";

  propagatedBuildInputs = [
    cadquery
    cq-apply-to-each-face
    cq-wild
  ];

}

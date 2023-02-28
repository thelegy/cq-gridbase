{ buildPythonPackage
, cadquery
, cq-wild
}:

buildPythonPackage {

  name = "cq-gridbase";

  src = ./.;
  format = "pyproject";

  propagatedBuildInputs = [
    cadquery
    cq-wild
  ];

}

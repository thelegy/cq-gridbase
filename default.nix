{ buildPythonPackage
, cadquery
}:

buildPythonPackage {

  name = "cq-gridbase";

  src = ./.;
  format = "pyproject";

  propagatedBuildInputs = [
    cadquery
  ];

}

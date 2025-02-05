# proserver-init.rb
class ProserverInit < Formula
  include Language::Python::Virtualenv
  desc "A Python script that facilitates setting up a Punkt.de Ansible project"
  homepage "https://punkt.de"

  head "https://github.com/punktDe/proserver-init", :using => :git, :branch => "main"

  url "https://github.com/punktDe/proserver-init", :using => :git, :tag => "0.3.0"

  depends_on "python@3.12"
  depends_on "uv"
  depends_on "pre-commit"
  depends_on "yq"

  resource "ruamel.yaml" do
    url "https://files.pythonhosted.org/packages/29/81/4dfc17eb6ebb1aac314a3eb863c1325b907863a1b8b1382cdffcb6ac0ed9/ruamel.yaml-0.18.6.tar.gz"
    sha256 "8b27e6a217e786c6fbe5634d8f3f11bc63e0f80f6a5890f28863d9c45aac311b"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/d9/e9/cf9ef5245d835065e6673781dbd4b8911d352fb770d56cf0879cf11b7ee1/rich-13.9.3.tar.gz"
    sha256 "bc1e01b899537598cf02579d2b9f4a415104d3fc439313a7a2c165d76557a08e"
  end

  def install
    virtualenv_install_with_resources
  end


end

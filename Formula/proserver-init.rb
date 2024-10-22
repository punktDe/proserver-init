# proserver-init.rb
class ProserverInit < Formula
  desc "A Python script that facilitates setting up a Punkt.de Ansible project"
  homepage "https://punkt.de"

  head "git@git.punkt.de:pt/proserver-init.git", :using => :git, :branch => "main"

  url "git@git.punkt.de:pt/proserver-init.git", :using => :git, :tag => "1.2.0"

  depends_on "python@3"

  def install
    bin.install "proserver-init"  # CHANGEME
  end

end

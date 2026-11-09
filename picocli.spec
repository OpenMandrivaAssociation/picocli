Name:		picocli
Version:	4.7.7
Release:	1
Summary:	Command line parser for Java
Group:		Development/Java
License:	ASL 2.0
URL:		https://picocli.info/
# The git tag also ships gradle-wrapper.jar and prebuilt junit, jansi,
# hamcrest, and system-rules jars. Those are removed from this archive.
Source0:	https://github.com/remkop/picocli/archive/refs/tags/v%{version}.tar.gz#/picocli-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar

%description
picocli parses command-line arguments. Groovy 3.0.22 uses it from
FileSystemCompiler and GroovyMain. Gradle's default distribution is
that Groovy. The annotation API matches the 4.6.3 pin. 4.7.7 fixes
ArgGroup options being added twice inside a Mixin, and HelpCommand
now returns the usage-help exit code.

%prep
%autosetup -n picocli-%{version}

%build
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
mkdir -p classes
find src/main/java -name '*.java' > sources.list
javac --release 8 -encoding UTF-8 -Xlint:-options -d classes @sources.list
# Keep module-info at the jar root. Putting it under META-INF/versions
# makes jar --describe-module print "releases:" and the generator
# turns that into a jmod(releases:) provide.
javac --release 9 --patch-module info.picocli=classes \
	-d classes \
	src/main/java9/module-info.java
jar cf %{name}.jar -C classes .
cat > %{name}.pom <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>info.picocli</groupId>
  <artifactId>picocli</artifactId>
  <version>%{version}</version>
  <name>picocli</name>
  <description>Command line parser for Java.</description>
  <url>https://picocli.info/</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%check
export JAVA_HOME=%{_jvmdir}/java-openjdk
export PATH=$JAVA_HOME/bin:$PATH
mkdir -p check
cat > check/Hello.java <<'END'
import picocli.CommandLine;
import picocli.CommandLine.Command;
import picocli.CommandLine.Option;
import picocli.CommandLine.Parameters;

@Command(name = "hello")
class Hello implements Runnable {
	@Option(names = "-n") String name = "world";
	@Parameters String extra;
	public void run() {}
	public static void main(String[] args) {
		Hello h = new Hello();
		new CommandLine(h).parseArgs("-n", "gradle", "x");
		if (!"gradle".equals(h.name) || !"x".equals(h.extra)) {
			throw new AssertionError(h.name + " " + h.extra);
		}
		System.out.println(CommandLine.VERSION);
	}
}
END
javac --release 8 -encoding UTF-8 -Xlint:-options -cp %{name}.jar -d check check/Hello.java
test "$(java -cp check:%{name}.jar Hello)" = %{version}

%install
sysjar install --buildroot %{buildroot} \
	--artifact %{name}.pom:%{name}.jar \
	--file-name %{name} \
	--filelist .mfiles

%files -f .mfiles
%doc LICENSE README.md

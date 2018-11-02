#!/usr/bin/env python3
import argparse, glob, importlib.util, inspect, ue4cli, subprocess, shlex, sys
from os.path import abspath, basename, dirname, exists, join
from collections import deque
from natsort import natsorted
import networkx as nx


# The default username used when building packages
DEFAULT_USER = 'adamrehn'


class Utility(object):
	'''
	Provides utility functionality
	'''
	
	@staticmethod
	def baseNames(classType):
		'''
		Returns the list of base class names for a class type
		'''
		return list([base.__name__ for base in classType.__bases__])
	
	@staticmethod
	def importFile(moduleName, filePath):
		'''
		Imports a Python module from a file
		'''
		
		# Temporarily add the directory containing the file to our search path,
		# in case the imported module uses relative imports
		moduleDir = dirname(filePath)
		sys.path.append(moduleDir)
		
		# Import the module
		spec = importlib.util.spec_from_file_location(moduleName, filePath)
		module = importlib.util.module_from_spec(spec)
		spec.loader.exec_module(module)
		
		# Restore the search path
		sys.path.remove(moduleDir)
		
		return module


class PackageBuilder(object):
	'''
	Provides functionality for building a set of Conan packages
	'''
	
	def __init__(self, rootDir, user, channel, profile, dryRun):
		self.rootDir = rootDir
		self.user = user
		self.channel = channel
		self.profile = profile
		self.dryRun = dryRun
	
	def execute(self, command):
		'''
		Executes the supplied command (or just prints it if we're in dry run mode)
		'''
		if self.dryRun == True:
			print(' '.join([shlex.quote(arg) for arg in command]), file=sys.stderr)
			return True
		else:
			return subprocess.call(command) == 0
	
	def listAvailablePackages(self):
		'''
		Retrieves the list of available packages (just the names, not the versions)
		'''
		allPackages = glob.glob(join(self.rootDir, '*', '*', 'conanfile.py'))
		uniqueNames = set([basename(dirname(dirname(p))) for p in allPackages])
		return list(uniqueNames)
	
	def identifyNewestVersion(self, name):
		'''
		Determines the newest version of a package and returns the identifier (name/version)
		'''
		
		# Attempt to retrieve the list of available versions for the package
		versions = natsorted([basename(dirname(v)) for v in glob.glob(join(self.rootDir, name, '*', 'conanfile.py'))])
		if len(versions) == 0:
			raise RuntimeError('no available versions for package "{}"'.format(name))
		
		return '{}/{}'.format(name, versions[-1])
	
	def parsePackage(self, package):
		'''
		Parses a package identifier (name/version) and returns the components
		'''
		return package.split('/', maxsplit=1)
	
	def stripQualifiers(self, package):
		'''
		Strips the username and channel from a fully-qualified package identifier
		'''
		return package.split('@', maxsplit=1)[0]
	
	def getConanfile(self, package):
		'''
		Retrieves the absolute path to the conanfile.py for a package, checking that it exists
		'''
		
		# Determine if we have a conanfile.py for the specified package
		name, version = self.parsePackage(package)
		conanfile = join(self.rootDir, name, version, 'conanfile.py')
		if not exists(conanfile):
			raise RuntimeError('no conanfile.py found for package "{}"'.format(package))
		
		return conanfile
	
	def extractDependencies(self, package):
		'''
		Retrieves the list of dependencies for a package
		'''
		
		# Import the conanfile and instantiate the first recipe class it contains
		module = Utility.importFile('conanfile', self.getConanfile(package))
		classes = inspect.getmembers(module, inspect.isclass)
		recipes = list([c[1] for c in classes if 'ConanFile' in Utility.baseNames(c[1])])
		recipe = recipes[0](None, None, user=self.user, channel=self.channel)
		
		# Extract the list of dependencies
		dependencies = list(recipe.requires)
		if hasattr(recipe, 'requirements'):
			setattr(recipe, 'requires', lambda d: dependencies.append(d))
			recipe.requirements()
		
		# Filter the dependencies to include only those we are building from our directory tree,
		# which will all use the same username and channel as the package that requires them
		dependencies = list([
			self.stripQualifiers(d)
			for d in dependencies
			if d.endswith('@{}/{}'.format(self.user, self.channel)) == True
		])
		return dependencies
	
	def buildDependencyGraph(self, packages):
		'''
		Builds the dependency graph for the specified list of packages
		'''
		
		# Create the DAG that will act as our dependency graph
		graph = nx.DiGraph()
		
		# Iteratively process our list of packages
		toProcess = deque(packages)
		while len(toProcess) > 0:
			
			# Add the current package to the graph
			current = toProcess.popleft()
			graph.add_node(current)
			
			# Retrieve the dependencies for the package and add them to the graph
			deps = self.extractDependencies(current)
			for dep in deps:
				graph.add_node(dep)
				graph.add_edge(dep, current)
				toProcess.append(dep)
		
		return graph
	
	def buildPackage(self, package):
		'''
		Builds an individual package
		'''
		packageDir = dirname(self.getConanfile(package))
		if self.execute(['conan', 'create', packageDir, '{}/{}'.format(self.user, self.channel), '--profile', self.profile]) == False:
			raise RuntimeError('failed to build package "{}"'.format(package))
	
	def uploadPackage(self, package, remote):
		'''
		Uploads the specified package to the specified remote
		'''
		fullyQualified = '{}@{}/{}'.format(package, self.user, self.channel)
		if self.execute(['conan', 'upload', fullyQualified, '--all', '--confirm', '-r', remote]) == False:
			raise RuntimeError('failed to upload package "{}" to remote "{}"'.format(fullyQualified, remote))
	
	def computeBuildOrder(self, packages):
		'''
		Builds the dependency graph for the specified list of packages and computes the build order
		'''
		
		# Build the dependency graph for the packages
		graph = self.buildDependencyGraph(packages)
		
		# Perform a topological sort to determine the build order
		return list(nx.topological_sort(graph))
	
	def buildPackages(self, buildOrder):
		'''
		Builds a list of packages using a pre-computed build order
		'''
		for package in buildOrder:
			print('\nBuilding package "{}"...'.format(package))
			self.buildPackage(package)
	
	def uploadPackages(self, packages, remote):
		'''
		Uploads the specified list of packages to the specified remote
		'''
		for package in packages:
			print('\nUploading package "{}"...'.format(package))
			self.uploadPackage(package, remote)


# Our supported command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true', help='Print Conan commands instead of running them')
parser.add_argument('-user', default=DEFAULT_USER, help='Set the user for the built packages (default user is "{}")'.format(DEFAULT_USER))
parser.add_argument('-upload', default=None, metavar='REMOTE', help='Upload the built packages to the specified Conan remote')
parser.add_argument('package', nargs='+', help='Package(s) to build, in either NAME or NAME==VERSION format (specify "all" to build all available packages)')

# If no command-line arguments were supplied, display the help message and exit
if len(sys.argv) < 2:
	parser.print_help()
	sys.exit(0)

# Parse the supplied command-line arguments
args = parser.parse_args()

# Retrieve the absolute path to the root of the directory tree containing our package recipes
rootDir = abspath(dirname(__file__))

# Query ue4cli for the UE4 version string and use the short form (4.XX) as the channel
ue4 = ue4cli.UnrealManagerFactory.create()
channel = ue4.getEngineVersion('short')

# Create our package builder
builder = PackageBuilder(rootDir, args.user, channel, 'ue4', args.dry_run)

# Process the specified list of packages, resolving versions as needed
packages = []
for arg in args.package:
	if arg.lower() == 'all':
		packages.extend(list([builder.identifyNewestVersion(p) for p in builder.listAvailablePackages()]))
	elif '==' in arg:
		packages.append(arg.replace('==', '/'))
	else:
		packages.append(builder.identifyNewestVersion(arg))

# Perform dependency resolution and compute the build order for the packages
buildOrder = builder.computeBuildOrder(packages)

# Report the computed build order to the user
uploadSuffix = ' and uploaded to the remote "{}"'.format(args.upload) if args.upload is not None else ''
print('\nThe following packages will be built{}:'.format(uploadSuffix))
for package in buildOrder:
	print('\t' + package)

# Attempt to build the packages
builder.buildPackages(buildOrder)

# If a remote has been specified to upload the built packages to, attempt to do so
if args.upload is not None:
	builder.uploadPackages(buildOrder, args.upload)

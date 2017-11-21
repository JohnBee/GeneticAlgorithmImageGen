from PIL import Image
from deap import base, creator, tools
from itertools import izip, chain, repeat
import sys
import math
import random

im = None
xsize, ysize = 0, 0


def roundup(x):
    """
    Round a given input to the nearest value of 10 and caps at 255.

    This function simplifies the learning as it reduces the matching accuracy.
    """
    a = int(math.ceil(x / 10.0)) * 10
    if a > 255:
        a = 255
    return a


def rgbIndiv():
    """
    Definition of an invidivual gene for the genetic algorithm.

    Each gene is initially list of size 3 for RGB value which are rounded to
    the nearest value of 10 for learning simplicity.
    """
    return [roundup(random.randint(0, 255)), roundup(random.randint(0, 255)),
            roundup(random.randint(0, 255))]


def pythag(a, b):
    """
    Calculate RGB distance squared.

    Returns distance between 2 RGB colours to determine how close they are.
    """
    return ((b[0]-a[0])**2 + (b[1]-a[1])**2 + (b[2]-a[2])**2)


def evalIndiv(individual):
    """
    Evaluate the individuals fitness.

    Compares the individual to the orignal image to see how close it matches.
    The closer the match the fitter the individual.
    """
    fit = 0
    for y in xrange(ysize):
        for x in xrange(xsize):
            r, g, b = im.getpixel((x, y))
            r, g, b = roundup(r), roundup(g), roundup(b)
            fit += pythag(individual[y*xsize + x], (r, g, b))
    return fit,


def mutate(individual, MUTX=0):
    """Mutate the individual by randomly adding or subtracting 10 RGB value."""
    for i, k in enumerate(individual):
        if random.random() < MUTX:
            x = random.randint(-1, 1)*10
            individual[i][random.randint(0, 2)] += x
    return individual,


def grouper(n, iterable, padvalue=None):
    """Group iterable in to groups of size n."""
    return izip(*[chain(iterable, repeat(padvalue, n-1))]*n)


def newImage(width, height):
    """Create and return a new image object."""
    return Image.new('RGB', (width, height), "white")


def loadImage(argv):
    """Load image from filename given."""
    im = Image.open(argv)
    return im


def saveFile(imObj, filename):
    """Save given image object to file."""
    imObj.save(filename + ".bmp", "BMP")


def outPutIndividual(individual, gen):
    """
    Write indiviudal to file.

    Transforms the given individual to an image format and saves to file.
    """
    outImg = newImage(xsize, ysize)
    outPix = outImg.load()

    for y in xrange(ysize):
        for x in xrange(xsize):
            outPix[x, y] = tuple(individual[y*xsize + x])
    saveFile(outImg, "out"+str(gen))


def main(filename):
    """
    Run the main genetic algorithm procedure.

    Generate a population of random images.
    Evaluate each individual by comparing to original image.
    Mate, mutate the individuals with a given probability MUTX and CXPB.
    Run until wanted fitness is achieved or max number of generations hit.
    Outut the best final individual.
    """
    global im, xsize, ysize
    im = loadImage(filename)
    xsize, ysize = im.size

    creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    toolbox = base.Toolbox()
    # Attribute generator
    toolbox.register("attr_indiv", rgbIndiv)
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual,
                     toolbox.attr_indiv, xsize*ysize)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evalIndiv)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate, MUTX=0.5)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=100)
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Extracting all the fitnesses of
    fits = [ind.fitness.values[0] for ind in pop]

    # Variable keeping track of the number of generations
    g = 0

    print max(fits)
    # Begin the evolution
    while max(fits) > 10000 and g < 100000:
        # A new generation
        g = g + 1
        print("-- Generation %i --" % g)
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring
        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)

        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)

        if g % 1000 == 0:
            print "Writing best individual to file"
            best_ind = tools.selBest(pop, 1)[0]
            outPutIndividual(best_ind, g)


CXPB = 0.2
MUTPB = 0.5
if __name__ == "__main__":
    main(main(sys.argv[1]))

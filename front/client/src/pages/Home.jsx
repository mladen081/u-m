function Home() {
  return (
    <main>
      <h1>The pattern concept</h1>
      <p>Design patterns help you learn from others' successes instead of your own failures.</p>
      <h2>What is a pattern?</h2>
      <p>Initially, you can think of a pattern as an especially clever and insightful
        way of solving a particular class of problems. That is, it looks like a lot of
        people have worked out all the angles of a problem and have come up with
        the most general, flexible solution for it. The problem could be one you
        have seen and solved before, but your solution probably didn't have the
        kind of completeness you'll see embodied in a pattern.
      </p>
      <p>
        Although they're called “design patterns,” they really aren't tied to the
        realm of design. A pattern seems to stand apart from the traditional way
        of thinking about analysis, design, and implementation. Instead, a pattern
        embodies a complete idea within a program, and thus it can sometimes
        appear at the analysis phase or high-level design phase. This is interesting
        because a pattern has a direct implementation in code and so you might
        not expect it to show up before low-level design or implementation (and in
        fact you might not realize that you need a particular pattern until you get
        to those phases).
      </p>
      <br />
      <p style={{ textAlign: 'right' }}><em>“Bruce Eckel”</em></p>
    </main>
  );
}

export default Home;
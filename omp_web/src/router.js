import { HashRouter as Router, Route, Switch, Redirect } from "react-router-dom";
import OmpLayout from "@/layouts";
import Login from "@/pages/Login";
import routerConfig from "@/config/router.config";
import HomePage from "@/pages/HomePage";

const OmpRouter = () => {
  let routerChildArr = routerConfig.map(item=>item.children).flat()
  return (
    <Router>
      <Switch>
        <Route path="/login" component={() => <Login />} />
        <Route
          path="/"
          component={() => (
            <OmpLayout>
              <Switch>
                <Route 
                  path="/homepage"
                  key="/homepage"
                  exact
                  render={()=><HomePage />}
                />
                {routerChildArr.map((item) => {
                  return (
                    <Route
                      path={item.path}
                      key={item.path}
                      exact
                      render={() => <item.component />}
                    />
                  );
                })}
                <Redirect exact path="/" to="/homepage"/>
              </Switch>
            </OmpLayout>
          )}
        />
        ]
      </Switch>
    </Router>
  );
};

export default OmpRouter;

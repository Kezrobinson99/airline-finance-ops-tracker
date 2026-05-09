# V6 Update - Airline-Specific Hub Market

This update changes hub ownership and hub buying logic.

## Hub Ownership Rules

- Monarch already owns: MAN, NCL
- Regal already owns: TPA, LAS
- Lauda already owns: VIE
- Monarch Cargo starts with no confirmed hub unless added later

## Hub Market Behaviour

When you select an airline on the Buy Assets page:

- The hub market only shows hubs that airline does NOT already own.
- Example: selecting Monarch will hide MAN and NCL.
- Example: selecting Regal will hide TPA and LAS.
- Example: selecting Lauda will hide VIE.

## Route Market Behaviour

You can still type a custom route such as:

```txt
MAN - JFK
```

The app should price it, let you buy it, then allow the route to be configured on the Routes page with aircraft type, frequency and pricing.
